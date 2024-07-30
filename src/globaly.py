import queue
import threading

ereignisse_queue = queue.Queue()
aufzeichnung = False
bool_dauerschleife = False
esc_flag = threading.Event()
stop_event = threading.Event()
