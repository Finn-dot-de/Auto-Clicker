# record.py

import time
import pyautogui
import pygetwindow as gw
from pynput import mouse, keyboard
import globals  # Importieren der globalen Variablen
import time
import ast
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import font as tkfont
from pynput import mouse, keyboard
import threading
import queue
import traceback
import pyautogui
import pygetwindow as gw

def press_windows_d():
    pyautogui.hotkey('win', 'd')

def bring_window_to_foreground(window_title):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window[0].activate()

def bei_klick(x, y, taste, gedrückt):
    if globals.aufzeichnung and gedrückt:
        globals.ereignisse_queue.put(('klick', time.time(), (x, y, taste.name)))

def bei_tastendruck(taste):
    if globals.aufzeichnung:
        try:
            ereignis_daten = taste.char if taste.char else str(taste)
            globals.ereignisse_queue.put(('tastendruck', time.time(), ereignis_daten))
        except AttributeError:
            globals.ereignisse_queue.put(('tastendruck', time.time(), str(taste)))
        if taste == keyboard.Key.esc:
            stoppe_aufzeichnung()
            return False

def bei_tastenfreigabe(taste):
    if globals.aufzeichnung:
        ereignis_daten = str(taste)
        globals.ereignisse_queue.put(('tastenfreigabe', time.time(), ereignis_daten))
        if taste == keyboard.Key.esc:
            return False

def starte_maus_listener():
    with mouse.Listener(on_click=bei_klick) as listener:
        listener.join()

def starte_tastatur_listener():
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenfreigabe) as listener:
        listener.join()

def starte_aufzeichnung():
    globals.aufzeichnung = True
    globals.ereignisse_queue.queue.clear()
    press_windows_d()
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)
    maus_thread.start()
    tastatur_thread.start()

def stoppe_aufzeichnung():
    globals.aufzeichnung = False
    globals.stop_event.set()
    bring_window_to_foreground('Auto-Clicker')
    print("Aufzeichnung gestoppt.")
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if dateipfad:
        try:
            with open(dateipfad, 'w') as f:
                while not globals.ereignisse_queue.empty():
                    ereignis = globals.ereignisse_queue.get()
                    if ereignis[0] == 'tastendruck' and ereignis[2] == 'Key.esc':
                        continue
                    if ereignis[0] == 'tastenfreigabe' and ereignis[2] == 'Key.esc':
                        continue
                    f.write(f"{ereignis}\n")
            messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")
