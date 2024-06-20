import cv2
import pickle
from config import *
import numpy as np

def hands_mov(dictionary):
    keyboard = cv2.imread('output/keyboard.png')
    sorted_frames = []
    sorted_frames_time = []
    last_frame_introduced = -1

    # look for last event
    last_event = float('-inf')
    for char in ALL_KEYS:
        key_events_char = dictionary[char]
        for time_event, frames in key_events_char:
            if time_event > last_event:
                last_event = time_event

    prev_event_time = float('-inf')
    while prev_event_time != last_event:
        next_event_time = float('inf')
        for char in ALL_KEYS:
            key_events_char = dictionary[char]
            for time_event, frames in key_events_char:
                if time_event < next_event_time and time_event > prev_event_time:
                    next_event_time = time_event
                    next_event_frames = frames

        prev_event_time = next_event_time
        for time_frame, frame in next_event_frames:
            if time_frame > last_frame_introduced:
                sorted_frames.append(frame)
                sorted_frames_time.append(time_frame)
                last_frame_introduced = time_frame

    movs_index = [[], []]
    movs_middle = [[], []]
    movs_ring = [[], []]
    movs_pinky = [[], []]

    for frame in sorted_frames:
        for index, hand in enumerate(frame):
            bool = right(hand)
            if bool:
                index = 0
                if int(hand[PINKY_TIP].x*dictionary['res'][0]) < 600:
                    continue
            else:
                if int(hand[PINKY_TIP].x*dictionary['res'][0]) > 600:
                    continue
                index = 1
            movs_pinky[index].append((int(hand[PINKY_TIP].x*dictionary['res'][0]), int(hand[PINKY_TIP].y*dictionary['res'][1])))
            movs_ring[index].append((int(hand[RING_FINGER_TIP].x*dictionary['res'][0]), int(hand[RING_FINGER_TIP].y*dictionary['res'][1])))
            movs_middle[index].append((int(hand[MIDDLE_FINGER_TIP].x*dictionary['res'][0]), int(hand[MIDDLE_FINGER_TIP].y*dictionary['res'][1])))
            movs_index[index].append((int(hand[INDEX_FINGER_TIP].x*dictionary['res'][0]), int(hand[INDEX_FINGER_TIP].y*dictionary['res'][1])))
    keyboard_copy = keyboard.copy()
    for index in range(0, 2):
        print(index)
        hand_contour = np.array(movs_pinky[index], dtype=np.int32)
        cv2.polylines(keyboard_copy, [hand_contour], isClosed=False, color=TIP_TO_COLOR[PINKY_TIP], thickness=2)
        
        hand_contour = np.array(movs_ring[index], dtype=np.int32)
        cv2.polylines(keyboard_copy, [hand_contour], isClosed=False, color=TIP_TO_COLOR[RING_FINGER_TIP], thickness=2)

        hand_contour = np.array(movs_middle[index], dtype=np.int32)
        cv2.polylines(keyboard_copy, [hand_contour], isClosed=False, color=TIP_TO_COLOR[MIDDLE_FINGER_TIP], thickness=2)

        hand_contour = np.array(movs_index[index], dtype=np.int32)
        cv2.polylines(keyboard_copy, [hand_contour], isClosed=False, color=TIP_TO_COLOR[INDEX_FINGER_TIP], thickness=2)

    cv2.imwrite(f'hand_movements.png', keyboard_copy)


if __name__ == '__main__':
    with open('output/all_data.pickle', 'rb') as f:
        dictionary = pickle.load(f)

    hands_mov(dictionary=dictionary)