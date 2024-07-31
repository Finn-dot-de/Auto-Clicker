# record.py

import time
import queue
import threading
from pynput import mouse, keyboard
import pyautogui
import pygetwindow as gw

# Globale Variablen
ereignisse_queue = queue.Queue()
aufzeichnung = False
stop_event = threading.Event()

def press_windows_d():
    pyautogui.hotkey('win', 'd')

def bring_window_to_foreground(window_title):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window[0].activate()

def bei_klick(x, y, taste, gedrückt):
    if aufzeichnung and gedrückt:
        ereignisse_queue.put(('klick', time.time(), (x, y, taste.name)))

def bei_tastendruck(taste):
    if aufzeichnung:
        try:
            ereignis_daten = taste.char if taste.char else str(taste)
            ereignisse_queue.put(('tastendruck', time.time(), ereignis_daten))
        except AttributeError:
            ereignisse_queue.put(('tastendruck', time.time(), str(taste)))
        if taste == keyboard.Key.esc:
            stoppe_aufzeichnung()
            return False

def bei_tastenfreigabe(taste):
    if aufzeichnung:
        ereignis_daten = str(taste)
        ereignisse_queue.put(('tastenfreigabe', time.time(), ereignis_daten))
        if taste == keyboard.Key.esc:
            return False

def starte_maus_listener():
    with mouse.Listener(on_click=bei_klick) as listener:
        listener.join()

def starte_tastatur_listener():
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenfreigabe) as listener:
        listener.join()

def starte_aufzeichnung():
    global aufzeichnung
    aufzeichnung = True
    ereignisse_queue.queue.clear()
    press_windows_d()
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)
    maus_thread.start()
    tastatur_thread.start()

def stoppe_aufzeichnung():
    global aufzeichnung
    aufzeichnung = False
    stop_event.set()
    bring_window_to_foreground('Auto-Clicker')  # Ersetze 'Auto-Clicker' durch den tatsächlichen Titel deines Fensters
    print("Aufzeichnung gestoppt.")
