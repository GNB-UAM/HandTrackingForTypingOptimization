import pickle
import cv2
import numpy as np

def video_char(dictionary, chars):
    keyboard = cv2.imread('output/keyboard.png')
    for char in chars:
        # Configura el objeto VideoWriter
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # Codec de video
        fps = 30  # Número de cuadros por segundo
        video_writer = cv2.VideoWriter(f"report_images/{char}.avi", fourcc, fps, (int(dictionary['res'][0]), int(dictionary['res'][1])))

        # print(dictionary)
        for time_event, array_event in dictionary[char]:
            # print(f"{time_event} ==> {array_event}")
            for time_frame, frame_processed in array_event:
                # black_frame = np.zeros((int(dictionary['res'][1]), int(dictionary['res'][0]), 3), dtype=np.uint8)
                keyboard_copy = keyboard.copy()
                for hand in frame_processed:
                    hand_contour = []
                    for point in hand:
                        #print(point.x)
                        hand_contour.append((int(point.x*dictionary['res'][0]), int(point.y*dictionary['res'][1])))
                    #print(hand_contour)
                    # Convert the list of points to a NumPy array
                    hand_contour = np.array(hand_contour, dtype=np.int32)
                    cv2.polylines(keyboard_copy, [hand_contour], isClosed=True, color=(0, 255, 0), thickness=2)
                video_writer.write(keyboard_copy)
                #cv2.imshow('Hand Tracking', keyboard_copy)
                #cv2.waitKey(1)
        video_writer.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    path = ''
    with open(path, 'rb') as f:
        dictionary = pickle.load(f)
    video_char(dictionary, ['a', 'z'])