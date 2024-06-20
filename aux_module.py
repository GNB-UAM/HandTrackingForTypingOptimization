from pynput import keyboard as kb
from typing import Dict, Tuple
import queue
import multiprocessing
import cv2
import os
import time
from config import *
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks.python import vision
import mediapipe as mp
import numpy as np

def get_keyboard_coordinates(camera_queue: multiprocessing.Queue, kd_queue: multiprocessing.Queue, resolution) -> Dict[str, Tuple[float, float]]:
    coords_keyboard: dict[str, tuple[float, float]] = dict()
    essential_keys = ['q', 'p', 'a', 'ñ', 'z', 'm']

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

    while not kd_queue.empty():
        kd_queue.get()

    # go through essential keys in pairs
    for i in range(0, len(essential_keys), 2):
        first_key = essential_keys[i]
        second_key = essential_keys[i + 1]
        cont_loop1 = True
        while cont_loop1:
            print("Press '" + first_key.upper() +"' with the forefinger of your right hand.")
            while True:
                try:
                    # It has to keep emptying the queue
                    instant_frame, frame = camera_queue.get()
                    bool_right_hand = False
                    try:
                        instant_kd, key_pressed = kd_queue.get_nowait()
                        if key_pressed == kb.KeyCode.from_char(first_key):
                            if (instant_frame - instant_kd) < EXPECTED_DELAY:
                                while (instant_frame - instant_kd) < EXPECTED_DELAY:
                                    instant_frame, frame = camera_queue.get()

                            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                            result = detector.detect(mp_image)
                            for hand_coords in result.hand_landmarks:
                                # Right hand
                                bool_right_hand = right(hand_coords)
                                if bool_right_hand:
                                    coords_keyboard[first_key] = hand_coords[INDEX_FINGER_TIP].x * resolution[0], hand_coords[INDEX_FINGER_TIP].y * resolution[1]
                                    cont_loop1 = False
                                    break
                            if not bool_right_hand:
                                print("Couldn't make a detection of the right hand. Please try again")
                            break
                        elif key_pressed == kb.Key.esc:
                            return None
                        else:
                            print(f"You didn't press the key {first_key}")
                            break
                    except queue.Empty:
                        pass
                    
                except queue.Empty:
                    pass

        cont_loop1 = True
        while cont_loop1:
            print("Press '" + second_key.upper() +"' with the forefinger of your right hand.")
            while True:
                try:
                    # It has to keep emptying the queue
                    instant_frame, frame = camera_queue.get()
                    try:
                        bool_right_hand = False
                        instant_kd, key_pressed = kd_queue.get_nowait()
                        if key_pressed == kb.KeyCode.from_char(second_key):
                            if (instant_frame - instant_kd) < EXPECTED_DELAY:
                                while (instant_frame - instant_kd) < EXPECTED_DELAY:
                                    instant_frame, frame = camera_queue.get()

                            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                            result = detector.detect(mp_image)
                            for hand_coords in result.hand_landmarks:
                                # Right hand
                                bool_right_hand = right(hand_coords)
                                if bool_right_hand:
                                    coords_keyboard[second_key] = hand_coords[PINKY_TIP].x * resolution[0], hand_coords[PINKY_TIP].y * resolution[1]
                                    cont_loop1 = False
                                    break
                            if not bool_right_hand:
                                print("Couldn't make a detection of the right hand. Please try again")
                            break
                        elif key_pressed == kb.Key.esc:
                            return None
                        else:
                            print(f"You didn't press the key {second_key}")
                            break
                    except queue.Empty:
                        pass
                    
                except queue.Empty:
                    pass

    avg_dist_x = 0
    for row in ALL_KEYS_BY_ROWS:
        if row[0] == 'q':
            interval_x = (coords_keyboard['q'][0] - coords_keyboard['p'][0])/(len(row)-1)
            interval_y = (coords_keyboard['q'][1] - coords_keyboard['p'][1])/(len(row)-1)
            avg_dist_x += interval_x
        elif row[0] == 'a':
            interval_x = (coords_keyboard['a'][0] - coords_keyboard['ñ'][0])/(len(row)-1)
            interval_y = (coords_keyboard['a'][1] - coords_keyboard['ñ'][1])/(len(row)-1)
            avg_dist_x += interval_x
        elif row[0] == 'z':
            interval_x = (coords_keyboard['z'][0] - coords_keyboard['m'][0])/(len(row)-1)
            interval_y = (coords_keyboard['z'][1] - coords_keyboard['m'][1])/(len(row)-1)
            avg_dist_x += interval_x
        for idx in range(len(row)):
            coords_keyboard[row[idx]] = (coords_keyboard[row[0]][0] - (interval_x * idx), coords_keyboard[row[0]][1] - (interval_y * idx))
    coords_keyboard['avg_dist'] = abs(avg_dist_x/3)
    return coords_keyboard