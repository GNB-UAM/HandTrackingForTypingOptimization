import cv2
import pickle
from config import *
import numpy as np
import time
import matplotlib.pyplot as plt
import random

def generate_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def prev_mov(keyboardevents, keyboard):
    #print(frames_proc)
    for key in ALL_KEYS:
        print(key)
        keyboard_copy = keyboard.copy()
        correct_hand, correct_tip = OPTIMAL_CLICK[key]
        if len(keyboardevents[key])>0:
            for instant_event, frames in keyboardevents[key]:
                movs = []
                for instante_frame, frame in frames:
                    if instante_frame - instant_event < EXPECTED_DELAY:
                        for hand in frame:
                            if correct_hand(hand):
                                movs.append((int(hand[correct_tip].x*keyboardevents['res'][0]), int(hand[correct_tip].y*keyboardevents['res'][1])))
                    else:
                        break
                if len(movs) > 1:
                    hand_contour = np.array(movs, dtype=np.int32)
                    color = generate_random_color()
                    cv2.circle(keyboard_copy, tuple(hand_contour[0]), radius=2, color=color, thickness=-1)
                    cv2.polylines(keyboard_copy, [hand_contour], isClosed=False, color=color, thickness=2)
                    #cv2.arrowedLine(keyboard_copy, tuple(hand_contour[0]), tuple(hand_contour[-1]), color=(255, 255, 255), thickness=3, tipLength=3)
                    cv2.imwrite(f'report_images/{key}_prev_mov.png', keyboard_copy)

if __name__ == '__main__':
    path = ''
    with open(path, 'rb') as f:
        dictionary = pickle.load(f)
    keyboard = cv2.imread('output/keyboard.png')
    prev_mov(keyboardevents = dictionary, keyboard = keyboard)