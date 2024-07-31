# record.py

import time
import pyautogui
import pygetwindow as gw
from pynput import mouse, keyboard
from src.globals import *
import time
from tkinter import messagebox, filedialog
from pynput import mouse, keyboard
import threading
import pyautogui
import pygetwindow as gw

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
    if globals.aufzeichnung:
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
    aufzeichnung = True
    ereignisse_queue.queue.clear()
    press_windows_d()
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)
    maus_thread.start()
    tastatur_thread.start()

def stoppe_aufzeichnung():
    aufzeichnung = False
    stop_event.set()
    bring_window_to_foreground('Auto-Clicker')
    print("Aufzeichnung gestoppt.")
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if dateipfad:
        try:
            with open(dateipfad, 'w') as f:
                while not ereignisse_queue.empty():
                    ereignis = globals.ereignisse_queue.get()
                    if ereignis[0] == 'tastendruck' and ereignis[2] == 'Key.esc':
                        continue
                    if ereignis[0] == 'tastenfreigabe' and ereignis[2] == 'Key.esc':
                        continue
                    f.write(f"{ereignis}\n")
            messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")
