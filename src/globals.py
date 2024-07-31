# globals.py

import queue
import threading

# Globale Variablen
ereignisse_queue = queue.Queue()
aufzeichnung = False
bool_dauerschleife = False
esc_flag = threading.Event()
stop_event = threading.Event()
