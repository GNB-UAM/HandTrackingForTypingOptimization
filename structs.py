from typing import List, Tuple
import config
from collections import deque
import time

class KeyboardEvent:
    def __init__(self, char: str, time: float):
        self.char = char
        self.time = time
        self.assoc_frames: List[Tuple[float, List]] = []

        self.clear_frames = [] #only used with verbose
    
    def __str__(self):
        return f"Keyboard Event: {self.char} {self.time}"

class KeyboardEventSet:
    def __init__(self):
        self.events: deque[KeyboardEvent] = deque() # deque with older events at left

    def add_event(self, event: KeyboardEvent):
        self.events.append(event)
    
    def remove_events(self, timestamp: float) -> List[KeyboardEvent]:
        ret = []
        while self.events and not (timestamp - self.events[0].time <= config.TIME_RANGE_DISCARD):
            #pop from left
            ret.append(self.events.popleft())
        
        return ret