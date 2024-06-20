import cv2
import mediapipe as mp
import numpy as np
import time
import signal
import sys
from multiprocessing import Queue, Event
from pynput import keyboard as kb
import config
import json

def record(frame_queue: Queue, pause_event: Event):
    def handler(signum, frame):
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        sys.exit()

    signal.signal(signal.SIGINT, handler)

    cap = cv2.VideoCapture(0)
    n_frames = 0

    print("Taking photo of the keyboard...")
    time.sleep(2)
    ret, frame = cap.read()
    frame_queue.put(((cap.get(3), cap.get(4)), cv2.flip(frame, 1)))
    print("Done!")

    while True:
        if not pause_event.is_set():
            ret, frame = cap.read()
            n_frames += 1
            if not ret:
                break

            frame_queue.put((time.time(), cv2.flip(frame, 1)))