from mediapipe.framework.formats import landmark_pb2
from structs import KeyboardEvent, KeyboardEventSet
from mediapipe.tasks.python import vision
from pynput import keyboard as kb
from typing import List, Tuple
from math import sqrt
from config import *
import multiprocessing
import queue
import threading
import cv2
import time
import datetime
import mediapipe as mp
import pickle
import json
import signal

report = {}
for key in ALL_KEYS:
    report[key] = {'OK': [], 'BAD': []}

def create_report(event_queue: multiprocessing.Queue, coords_keyboard: dict, resolution: Tuple[int, int]):
    while True:
        event = event_queue.get()
        if event is None:
            break
        for time_frame, processed_hands in event.assoc_frames:
            correct_finger = False
            dif = time_frame - event.time
            init = EXPECTED_DELAY - 0.05
            end = EXPECTED_DELAY + 0.05
            if dif > init and end < 0.15:
                hand_function, correct_finger_idx = OPTIMAL_CLICK[event.char]
                x_char, y_char = coords_keyboard[event.char]
                avg_dist = coords_keyboard['avg_dist']
                x_finger = -1
                y_finger = -1

                # Check if the correct finger tapped the key
                for hand in processed_hands:
                    correct_hand_bool = hand_function(hand)
                    if correct_hand_bool:
                        x_finger = hand[correct_finger_idx].x * resolution[0]
                        y_finger = hand[correct_finger_idx].y * resolution[1]
                        if sqrt((x_char - x_finger) ** 2 + (y_char - y_finger) ** 2) < avg_dist*2/3:
                            report[event.char]['OK'].append((x_finger, y_finger))
                            correct_finger = True

                if not correct_finger:
                    nearest_dist = float('inf')
                    nearest_tip = None
                    hand_name_click = ''
                    #look for finger that tapped the key
                    for hand in processed_hands:
                        hand_name_v = hand_name(hand)
                        for finger_tip_idx in ALL_TIPS:
                            x_tip = hand[finger_tip_idx].x * resolution[0]
                            y_tip = hand[finger_tip_idx].y * resolution[1]
                            dist = sqrt((x_char - x_tip) ** 2 + (y_char - y_tip) ** 2)
                            if dist < avg_dist/2 and dist < nearest_dist:
                                nearest_dist = dist
                                nearest_tip = finger_tip_idx
                                hand_name_click = hand_name_v
                                x_near = x_tip
                                y_near = y_tip
                    if nearest_dist < float('inf'): #if found one
                        report[event.char]['BAD'].append(((x_finger, y_finger), hand_name_click, nearest_tip, (x_near, y_near)))
                    else:
                        report[event.char]['BAD'].append(((x_finger, y_finger), '', -1, (-1, -1)))
                break

    percentages = {}
    for key in ALL_KEYS:
        good = 0
        bad = 0
        not_sure = 0
        if len(report[key]['OK'])>0 or len(report[key]['BAD'])>0:
            for click in report[key]['OK']:
                good += 1
            for click in report[key]['BAD']:
                finger_correct = click[0]
                if finger_correct[0] > 0:
                    bad += 1
                else:
                    not_sure += 1
            total = good + bad + not_sure
            percentages[key] = {'good': good/total, 'bad': bad/total, 'not_sure': not_sure/total}
        else:
            percentages[key] = {'good': -1, 'bad': -1, 'not_sure': -1}
    
    for key in ALL_KEYS:
        if percentages[key]['good'] > -1:
            if percentages[key]['bad'] > 0.25:
                print(f"{RED_INIT}The key {key} has been tapped bad more than a fourth of the times!! ({percentages[key]['bad']}){RED_END}")
            elif percentages[key]['good'] == 1:
                print(f"{GREEN_INIT}Congratulations!! The key {key} has been tapped correctly every time!!{GREEN_END}")

    with open("output/report.json", 'w') as f:
        json.dump(report, f)


def map(kd_queue: multiprocessing.Queue, frame_buffer: multiprocessing.Queue, resolution:Tuple, coords_keyboard: dict, verbose: bool):
    # Ignore SIGINT Signals. This process will end when it stop receiving signals
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    dictionary = dict()
    dictionary['res'] = resolution
    dictionary['coords_keyboard'] = coords_keyboard

    all_keys_code = []
    for key in ALL_KEYS:
        dictionary[key] = []
        all_keys_code.append(kb.KeyCode.from_char(key))

    event_set = KeyboardEventSet()

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options = mp.tasks.BaseOptions(model_asset_path="hand_landmarker.task"), # path to model
        running_mode = mp.tasks.vision.RunningMode.IMAGE, # running on a live stream
        num_hands = 2, # track both hands
        min_hand_detection_confidence = 0.3, # lower than value to get predictions more often
        min_hand_presence_confidence = 0.3, # lower than value to get predictions more often
        min_tracking_confidence = 0.3, # lower than value to get predictions more often
    )
    # initialize landmarker
    detector = vision.HandLandmarker.create_from_options(options)

    if verbose:
        coordinates = (50, 50)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2

    event_queue = multiprocessing.Queue(maxsize=-1)
    report_thread = None
    report_thread = threading.Thread(target=create_report, args=(event_queue, coords_keyboard, resolution, ))
    report_thread.start()

    while True:
        try:
            instant_frame, frame = frame_buffer.get(timeout=5)
            while True:
                try:
                    instant_kd, key = kd_queue.get_nowait()
                    if key == kb.Key.esc:
                        break
                    if key in all_keys_code:
                        event = KeyboardEvent(key.char, instant_kd)
                        event_set.add_event(event)
                except queue.Empty:
                    pass

                # Condition to stop adding possible events that are interesting for this frame
                if time.time() - instant_frame > TIME_RANGE_DISCARD:
                    break
            
            # Remove old enough events
            removed_events = event_set.remove_events(instant_frame)
            for event_removed in removed_events:
                event_queue.put((event_removed))
                dictionary[event_removed.char].append((event_removed.time, event_removed.assoc_frames))
                if verbose: #write video to disk the clear video
                    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
                    out = cv2.VideoWriter(f'videos/{event_removed.char}{event_removed.time}.avi', fourcc, 27.0, frameSize=(int(resolution[0]), int(resolution[1])))
                    for instant_frame_event_removed, frame_event_removed in event_removed.clear_frames:
                        dim_text, _ = cv2.getTextSize(f"{instant_frame_event_removed}", font, scale, thickness)
                        coords_rect = (coordinates[0], coordinates[1] - dim_text[1])
                        frame_event_removed = cv2.rectangle(frame_event_removed, coords_rect, (coordinates[0] + dim_text[0], coordinates[1]), (255, 255, 255), cv2.FILLED)
                        frame_text = cv2.putText(frame_event_removed, f"{instant_frame_event_removed}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
                        out.write(frame_text)
                    out.release()

            # Try to associate the frame to the events
            # check if there is any associable in the range
            valid_frame = False
            for event in event_set.events:
                if abs(event.time - instant_frame) < TIME_RANGE:
                    valid_frame = True
                    break

            if valid_frame:
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                result = detector.detect(mp_image)
                for event in event_set.events:
                    if abs(instant_frame - event.time) < TIME_RANGE:
                        #inside range --> append processed frame to keyboard event
                        event.assoc_frames.append((instant_frame, result.hand_landmarks))
                        if verbose:
                            event.clear_frames.append((instant_frame, frame))

        except queue.Empty:
            break

    # Remove old enough events
    removed_events = event_set.remove_events(float('inf'))
    for event_removed in removed_events:
        event_queue.put((event_removed))
        dictionary[event_removed.char].append((event_removed.time, event_removed.assoc_frames))
        if verbose:
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            out = cv2.VideoWriter(f'videos/{event_removed.char}{event_removed.time}.avi', fourcc, 27.0, frameSize=(1080, 720))
            for instant_frame, frame in event_removed.clear_frames:
                dim_text, _ = cv2.getTextSize(f"{instant_frame}", font, scale, thickness)
                coords_rect = (coordinates[0], coordinates[1] - dim_text[1])
                frame = cv2.rectangle(frame, coords_rect, (coordinates[0] + dim_text[0], coordinates[1]), (255, 255, 255), cv2.FILLED)
                frame_text = cv2.putText(frame, f"{instant_frame}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
                out.write(frame_text)
            out.release()

    event_queue.put(None)

    report_thread.join()
    with open(f"output/all_data.pickle", "wb") as file:
        pickle.dump(dictionary, file)