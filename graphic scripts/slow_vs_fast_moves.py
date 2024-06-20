import json
import pickle
from config import *
import math
import matplotlib.pyplot as plt

def main(fast, slow):
    coords_keyboard = fast['coords_keyboard']
    res = fast['res']

    graph_times = []
    graph_distances = []

    plt.figure(figsize=(10, 5))
    for key in ALL_KEYS:
        coord_key_x, coord_key_y = coords_keyboard[key]
        print(key)
        for key_event_time, array in fast[key]:
            key_event_array_times = []
            key_event_array_distances = []
            print(array)

            for time_frame, frame_processed in array:
                for hand in frame_processed:
                    if right(hand) and abs(time_frame - key_event_time)<1:
                        x_tip = hand[INDEX_FINGER_TIP].x
                        y_tip = hand[INDEX_FINGER_TIP].y
                        dist = math.sqrt((coord_key_x - (x_tip*res[0])) ** 2 + (coord_key_y - (y_tip*res[0])) ** 2)

                        key_event_array_times.append(time_frame - key_event_time)
                        key_event_array_distances.append(dist)
            graph_times.append(key_event_array_times)
            graph_distances.append(key_event_array_distances)
            line_fast, = plt.plot(key_event_array_times, key_event_array_distances, linestyle='-', color='b', linewidth=0.5)

    
    #slow moves
    coords_keyboard = slow['coords_keyboard']
    res = slow['res']
    #print(fast['h'])

    graph_times = []
    graph_distances = []

    for key in ALL_KEYS:
        coord_key_x, coord_key_y = coords_keyboard[key]
        for key_event_time, array in slow[key]:
            key_event_array_times = []
            key_event_array_distances = []
            print(array)

            for time_frame, frame_processed in array:
                for hand in frame_processed:
                    if right(hand):
                        x_tip = hand[INDEX_FINGER_TIP].x
                        y_tip = hand[INDEX_FINGER_TIP].y
                        dist = math.sqrt((coord_key_x - (x_tip*res[0])) ** 2 + (coord_key_y - (y_tip*res[0])) ** 2)

                        key_event_array_times.append(time_frame - key_event_time)
                        key_event_array_distances.append(dist)
            graph_times.append(key_event_array_times)
            graph_distances.append(key_event_array_distances)
            line_slow, = plt.plot(key_event_array_times, key_event_array_distances, linestyle='-', color='r', linewidth=0.5)

    # Add titles and labels
    plt.legend([line_fast, line_slow],['Fast moves', 'Slow moves'], loc='upper right')
    plt.title('Distance of index finger to "a" ')
    plt.xlabel('Time(s)')
    plt.ylabel('Distance (pixels)')

    # Show
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    path_fast = ''
    with open(path_fast, 'rb') as f:
        fast = pickle.load(f)
    path_slow = ''
    with open(path_slow, 'rb') as f:
        slow = pickle.load(f)
    main()