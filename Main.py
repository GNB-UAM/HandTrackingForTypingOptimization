from keyboard_sensor import launch_listener
from camera import record
from aux_module import get_keyboard_coordinates
from processing_loop import map
import config
from pynput import keyboard as kb
import multiprocessing
import cv2
import os
import signal
import time
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import json
import threading

def main(verbose):
    multiprocessing.set_start_method('spawn')
    camera_queue = multiprocessing.Queue(maxsize=-1)
    kd_queue = multiprocessing.Queue(maxsize=-1)

    map_process: multiprocessing.Process = None
    cam_process: multiprocessing.Process = None
    kd_process: multiprocessing.Process = None

    def handler(signum, frame):
        stop_camera.set()
        while not camera_queue.empty():
            _, _ = camera_queue.get()
        if kd_process:
            if kd_process.is_alive():
                kd_process.join()
        if cam_process:
            if cam_process.is_alive():
                cam_process.join()
        if map_process:
            if map_process.is_alive():
                map_process.join()
        try:
            exit(0)
        except:
            pass

    signal.signal(signal.SIGINT, handler)

    #Create processes for camera and key detect
    stop_camera = multiprocessing.Event()
    cam_process = multiprocessing.Process(target=record, args=(camera_queue, stop_camera, ))
    kd_process = multiprocessing.Process(target=launch_listener, args=(kd_queue, ))

    # Start detection
    cam_process.start()
    kd_process.start()

    stop_camera.set()

    resolution, keyboard = camera_queue.get()
    cv2.imwrite(f'output/keyboard.png', keyboard)

    #Calibration loop
    coords_keyboard = None
    new_keyboard = False
    while True:
        if not new_keyboard:
            try:
                with open("keyboard.json", 'r') as json_file:
                    coords_keyboard = json.load(json_file)
            except:
                new_keyboard = True
        if new_keyboard or coords_keyboard is None:
            stop_camera.clear()
            coords_keyboard = get_keyboard_coordinates(camera_queue, kd_queue, resolution)
            if coords_keyboard is None:
                # Wait for the processes to finish
                stop_camera.set()
                kd_process.join()
                os.kill(cam_process.pid, signal.SIGINT)
                while not camera_queue.empty():
                    _, _ = camera_queue.get()
                cam_process.join()
                return 0

            stop_camera.set()
            with open("keyboard.json", 'w') as json_file:
                json.dump(coords_keyboard, json_file)
        
        keyboard_copy = keyboard.copy()

        for key in config.ALL_KEYS:
            x_char, y_char = coords_keyboard[key]
            _, tip = config.OPTIMAL_CLICK[key]
            radius = int(coords_keyboard['avg_dist'] * 2 / 3)
            cv2.circle(keyboard_copy, (int(x_char), int(y_char)), radius = radius, color = config.TIP_TO_COLOR[tip], thickness=1)
            cv2.putText(keyboard_copy, key, (int(x_char), int(y_char)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.TIP_TO_COLOR[tip], 1)
        
        text_size, _ = cv2.getTextSize("Press any key to close the window", cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        init_text_x = int(resolution[0]/2 - text_size[0]/2)
        init_text_y = 50
        init_rect = (init_text_x-5, int(init_text_y-text_size[1]/2-5))
        end_rect = (init_text_x+text_size[0]+5, int(init_text_y+text_size[1]/2))
        color = (0, 0, 0)
        keyboard_copy = cv2.rectangle(keyboard_copy, init_rect, end_rect, color, cv2.FILLED)
        color = (255, 255, 255)
        text = "Press any key to close the window"
        cv2.putText(keyboard_copy, text, (init_text_x, init_text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        cv2.imshow('Coordinates result',keyboard_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        # Discard keys to close the window or others
        time.sleep(0.5)
        while not kd_queue.empty():
            _, _ = kd_queue.get()
        
        while True:
            print("Are the coordinates ok? y/n")
            _, key = kd_queue.get()
            if key == kb.KeyCode.from_char('y'):
                print("Yes")
                new_keyboard = False
                break
            elif key == kb.KeyCode.from_char('n'):
                print("NO")
                new_keyboard = True
                break
        if not new_keyboard:
            break

    stop_camera.clear()
    # Start mapping process
    map_process = multiprocessing.Process(target=map, args=(kd_queue, camera_queue, (int(resolution[0]), int(resolution[1])), coords_keyboard, verbose))
    map_process.start()

    # Wait for the processes to finish
    kd_process.join()
    os.kill(cam_process.pid, signal.SIGINT)
    cam_process.join()
    map_process.join()

if __name__ == "__main__":
    #Uncomment to save videos associated to keyboard events
    #main(verbose = True)
    main(verbose = False)