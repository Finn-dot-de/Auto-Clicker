# replay.py

import time
import ast
import traceback
from pynput import mouse, keyboard
from tkinter import messagebox
from src.globals import *  # Importieren der globalen Variablen

def hole_taste(taste_str):
    print(f"Verarbeite Tastencode: {taste_str}")  # Debug-Ausgabe

    # Handle spezielle Tasten
    if taste_str.startswith('Key.'):
        try:
            return getattr(keyboard.Key, taste_str.split('.')[1])
        except AttributeError:
            print(f"Unbekannter Tastencode: {taste_str}")
            return None

    # Handle druckbare Zeichen
    elif len(taste_str) == 1 and taste_str.isprintable():
        return keyboard.KeyCode(char=taste_str)

    # Handle Maustasten
    elif taste_str in ['left', 'right', 'middle']:
        return getattr(mouse.Button, taste_str)

    # Unbekannte Tasten oder Zeichen
    else:
        print(f"Unbekannter Tastencode: {taste_str}")
        return None

def spiele_ereignisse_ab(dateipfad):
    global bool_dauerschleife
    try:
        with open(dateipfad, 'r') as f:
            ereignisse = [ast.literal_eval(line.strip()) for line in f]
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")
        traceback.print_exc()
        raise ValueError("Fehler beim Lesen der Datei")

    if not ereignisse:
        raise ValueError("Keine Ereignisse in der ausgewählten Datei.")

    maus_steuerung = mouse.Controller()
    tastatur_steuerung = keyboard.Controller()

    while True:
        print("Starte Ereigniswiedergabe...")  # Debug-Ausgabe
        start_zeit = ereignisse[0][1]

        for ereignis in ereignisse:
            if esc_flag.is_set() or stop_event.is_set():
                bool_dauerschleife = False
                break

            ereignis_typ, ereignis_zeit, ereignis_daten = ereignis
            verzögerung = ereignis_zeit - start_zeit
            time.sleep(verzögerung)
            start_zeit = ereignis_zeit

            try:
                if ereignis_typ == 'klick':
                    x, y, taste_name = ereignis_daten
                    taste = mouse.Button.left if taste_name == 'left' else mouse.Button.right
                    maus_steuerung.position = (x, y)
                    maus_steuerung.click(taste)
                elif ereignis_typ == 'tastendruck':
                    taste = hole_taste(ereignis_daten)
                    if taste is not None:
                        tastatur_steuerung.press(taste)
                elif ereignis_typ == 'tastenfreigabe':
                    taste = hole_taste(ereignis_daten)
                    if taste is not None:
                        tastatur_steuerung.release(taste)
            except Exception as e:
                print(f"Fehler beim Verarbeiten des Ereignisses {ereignis}: {e}")
                traceback.print_exc()

        if not bool_dauerschleife:
            break

    # Popup für das Ende des Replays
    print("Wiedergabe erfolgreich abgeschlossen!")  # Debug-Ausgabe
    messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")

def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()

def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:
        esc_flag.set()
        return False
