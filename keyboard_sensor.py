from pynput import keyboard as kb
import time
from multiprocessing import Queue
import signal

def pulse(key, queue: Queue):
	timestamp = time.time()
	if hasattr(key, 'char') and key.char is not None:
		lower_char = key.char.lower()

		key = kb.KeyCode.from_char(lower_char)
	queue.put((timestamp, key))
	if key == kb.Key.esc:
		return False

def launch_listener(queue: Queue):
	def handler(signum, frame):
		#Sentinel message
		queue.put((None, None))
		queue.close()
		queue.join_thread()
		exit(0)

	signal.signal(signal.SIGINT, handler)
	listener = kb.Listener(lambda key: pulse(key, queue))

	listener.start()
	while listener.is_alive():
		pass