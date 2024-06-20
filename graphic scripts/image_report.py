import json
import cv2
import config
import time
import pickle
from video_from_dicc import video_letra

GREEN_INIT = "\033[32m"
GREEN_END = "\033[0m"

RED_INIT = "\033[31m"
RED_END = "\033[0m"

def image_report(keyboard, report, diccionario):    
    with open('mano_ejemplo.pickle', 'rb') as f:
        mano_ejemplo = pickle.load(f)
    
    keyboard_img = cv2.imread('output/keyboard.png')

    avg_dist = keyboard['avg_dist']
    image_all = keyboard_img.copy()

    fraccion_mano = (diccionario['res'][0]/6, diccionario['res'][1]/3)
    _, start_point_y = (5*diccionario['res'][0]/6, 2*diccionario['res'][1]/3)
    
    for key in config.ALL_KEYS:
        image = keyboard_img.copy()
        draw_circle = False
        if len(report[key]['OK'])>0 or len(report[key]['BAD'])>0:
            #print(key)
            correct_x, correct_y = keyboard[key]
            _, finger_tip_idx = config.OPTIMAL_CLICK[key]
            for click in report[key]['OK']:
                if click[0] > 0:
                    draw_circle = True
                #cv2.circle(image, (int(click[0]), int(click[1])), radius = 4, color = (0, 255, 0), thickness=-1)
                cv2.putText(image, key, (int(click[0]), int(click[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), thickness=1)
                cv2.putText(image_all, key, (int(click[0]), int(click[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), thickness=1)
            for click in report[key]['BAD']:
                finger_correct = click[0]
                if finger_correct[0] > 0:
                    draw_circle = True
                hand = click[1]
                finger = click[2]
                coords_click = click[3]
                #print(click)
                if finger_correct[0] > 0:
                    #cv2.circle(image, (int(finger_correct[0]), int(finger_correct[1])), radius = 4, color = (0, 0, 255), thickness=-1)
                    cv2.putText(image, key, (int(finger_correct[0]), int(finger_correct[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), thickness=1)
                    cv2.putText(image_all, key, (int(finger_correct[0]), int(finger_correct[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), thickness=1)
                    if hand != '':
                        # cv2.circle(image, (int(finger_correct[0], int(finger_correct[1]))), radius = 2, color = (0, 255, 0), thickness=1)
                        cv2.putText(image, '+', (int(coords_click[0]), int(coords_click[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, config.TIP_TO_COLOR[finger] , thickness=1)
                        cv2.putText(image_all, '+', (int(coords_click[0]), int(coords_click[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, config.TIP_TO_COLOR[finger] , thickness=1)
                #elif hand != '':
                    # cv2.circle(image, (int(finger_correct[0], int(finger_correct[1]))), radius = 2, color = (0, 255, 0), thickness=1)
                #    cv2.putText(image, 'x', (int(coords_click[0]), int(coords_click[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, config.TIP_TO_COLOR[finger] , thickness=1)
            if draw_circle:
                cv2.circle(image, (int(correct_x), int(correct_y)), radius = int(avg_dist * 2 / 3), color = config.TIP_TO_COLOR[finger_tip_idx], thickness=1)
                cv2.circle(image_all, (int(correct_x), int(correct_y)), radius = int(avg_dist * 2 / 3), color = config.TIP_TO_COLOR[finger_tip_idx], thickness=1)

                for index, point in enumerate(mano_ejemplo.hand_landmarks[0]):
                    if index in config.ALL_TIPS:
                        color = config.TIP_TO_COLOR[index]
                        radius=10
                    else:
                        color = (255, 255, 255)
                        radius=5
                    #print((int(point.x*fraccion_mano[0]), int(point.y*fraccion_mano[1])))
                    cv2.circle(image, (int(point.x*fraccion_mano[0]), int(start_point_y + point.y*fraccion_mano[1])), radius = radius, color = color, thickness=-1)
            cv2.imwrite(f'report_images/{key}.png', image)
    
    for index, point in enumerate(mano_ejemplo.hand_landmarks[0]):
        if index in config.ALL_TIPS:
            color = config.TIP_TO_COLOR[index]
            radius=10
        else:
            color = (255, 255, 255)
            radius=5
        #print((int(point.x*fraccion_mano[0]), int(point.y*fraccion_mano[1])))
        cv2.circle(image_all, (int(point.x*fraccion_mano[0]), int(start_point_y + point.y*fraccion_mano[1])), radius = radius, color = color, thickness=-1)
    cv2.imwrite(f'report_images/all.png', image_all)


if __name__ == '__main__':
    try:
        with open("output/report.json", 'r') as json_file:
            report = json.load(json_file)
    except Exception as e:
        report = None
        pass
    
    try:
        with open("keyboard.json", 'r') as json_file:
            keyboard = json.load(json_file)
    except Exception as e:
        keyboard = None

    path = ''   
    with open(path, 'rb') as f:
        diccionario = pickle.load(f)
    if report and keyboard and diccionario:
        image_report(keyboard, report, diccionario)