from typing import Callable, Tuple, Dict, Any, List

'Time range to assign a frame to a keyboard event'
TIME_RANGE = 0.5
TIME_RANGE_DISCARD = TIME_RANGE * 1.5

EXPECTED_DELAY = 0.1

'Configuration of keyboard by rows'
ALL_KEYS_BY_ROWS = [
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ñ"],
    ["z", "x", "c", "v", "b", "n", "m"]
]

'All keys of keyboard without rows'
ALL_KEYS = [key for row in ALL_KEYS_BY_ROWS for key in row]

'Indexes for each tip in the coordinates detected by MediaPipe'
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20
ALL_TIPS = [THUMB_TIP, INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, RING_FINGER_TIP,PINKY_TIP]

'Dictionary to get the name of the finger from the index'
TIP_TO_FINGER: Dict[int, str] = {
    THUMB_TIP: 'thumb',
    INDEX_FINGER_TIP: 'index finger',
    MIDDLE_FINGER_TIP: 'middle finger',
    RING_FINGER_TIP: 'ring finger',
    PINKY_TIP: 'pinky'
}

'Dictionary to represent each finger'
TIP_TO_COLOR: Dict[int, Tuple[int, int, int]] = {
    THUMB_TIP: (255, 0, 0),
    INDEX_FINGER_TIP: (128, 128, 0),
    MIDDLE_FINGER_TIP: (128, 0, 128),
    RING_FINGER_TIP: (255, 255, 0),
    PINKY_TIP: (255, 0, 255)
}

'Function to know if it is Left hand'
def left(coords: List) -> bool:
    return coords[THUMB_TIP].x - coords[PINKY_TIP].x > 0

'Function to know if it is Right hand'
def right(coords: List) -> bool:
    return coords[THUMB_TIP].x - coords[PINKY_TIP].x < 0
    
'Function to get name of the hand'
def hand_name(coords: List) -> str:
    if coords[THUMB_TIP].x - coords[PINKY_TIP].x < 0:
        return 'right'
    else:
        return 'left'

'Dictionary to get the hand function and the index of the finger it must be pressed with of each key'
TypeCallable = Callable[[List], bool]
OPTIMAL_CLICK: Dict[Any, Tuple[TypeCallable, int]] = {
    'q': (left, PINKY_TIP),
    'w': (left, RING_FINGER_TIP),
    'e': (left, MIDDLE_FINGER_TIP),
    'r': (left, INDEX_FINGER_TIP),
    't': (left, INDEX_FINGER_TIP),
    'y': (right, INDEX_FINGER_TIP),
    'u': (right, INDEX_FINGER_TIP),
    'i': (right, MIDDLE_FINGER_TIP),
    'o': (right, RING_FINGER_TIP),
    'p': (right, PINKY_TIP),
    'a': (left, PINKY_TIP),
    's': (left, RING_FINGER_TIP),
    'd': (left, MIDDLE_FINGER_TIP),
    'f': (left, INDEX_FINGER_TIP),
    'g': (left, INDEX_FINGER_TIP),
    'h': (right, INDEX_FINGER_TIP),
    'j': (right, INDEX_FINGER_TIP),
    'k': (right, MIDDLE_FINGER_TIP),
    'l': (right, RING_FINGER_TIP),
    'ñ': (right, PINKY_TIP),
    'z': (left, PINKY_TIP),
    'x': (left, RING_FINGER_TIP),
    'c': (left, MIDDLE_FINGER_TIP),
    'v': (left, INDEX_FINGER_TIP),
    'b': (left, INDEX_FINGER_TIP),
    'n': (right, INDEX_FINGER_TIP),
    'm': (right, INDEX_FINGER_TIP)
}

'Macro to write green text'
GREEN_INIT = "\033[32m"
GREEN_END = "\033[0m"

'Macro to write red text'
RED_INIT = "\033[31m"
RED_END = "\033[0m"