# Importiert die benötigten Module und Bibliotheken
import ast  # Zum sicheren Parsen von Python-Ausdrücken aus Strings
import time  # Zum Arbeiten mit Zeitfunktionen
import traceback  # Zum Drucken von Tracebacks bei Ausnahmen
from tkinter import messagebox  # Zum Anzeigen von Popup-Nachrichten

from pynput import mouse, keyboard  # Zum Erfassen und Steuern von Maus- und Tastaturereignissen

from src.globals import *  # Importiert globale Variablen aus dem globals-Modul


# Funktion zum Konvertieren von Tastenzeichenfolgen in Tastenobjekte
def hole_taste(taste_str):
    print(f"Verarbeite Tastencode: {taste_str}")  # Debug-Ausgabe zur Überwachung der Tastencodes

    # Behandelt spezielle Tasten, die mit 'Key.' beginnen
    if taste_str.startswith('Key.'):
        try:
            # Versucht, die entsprechende Taste aus dem keyboard.Key-Objekt zu holen
            return getattr(keyboard.Key, taste_str.split('.')[1])
        except AttributeError:
            print(
                f"Unbekannter Tastencode: {taste_str}")  # Gibt eine Fehlermeldung aus, wenn die Taste nicht gefunden wird
            return None

    # Behandelt druckbare Zeichen (einzelne Buchstaben oder Symbole)
    elif len(taste_str) == 1 and taste_str.isprintable():
        return keyboard.KeyCode(char=taste_str)

    # Behandelt Maustasten (links, rechts, Mitte)
    elif taste_str in ['left', 'right', 'middle']:
        return getattr(mouse.Button, taste_str)

    # Behandelt unbekannte Tasten oder Zeichen
    else:
        print(f"Unbekannter Tastencode: {taste_str}")  # Gibt eine Fehlermeldung aus, wenn die Taste nicht erkannt wird
        return None


# Funktion zum Abspielen der Ereignisse aus einer Datei
def spiele_ereignisse_ab(dateipfad):
    bool_dauerschleife = os.environ.get('BOOL_DAUERSCHLEIFE', 'False') == 'True'
    print("replay.py>>>>>>>>>> ", bool_dauerschleife)
    try:
        with open(dateipfad, 'r') as f:  # Datei zum Lesen öffnen
            ereignisse = [ast.literal_eval(line.strip()) for line in f]  # Ereignisse aus der Datei lesen und parsen
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")  # Fehlermeldung ausgeben
        traceback.print_exc()  # Traceback drucken
        raise ValueError("Fehler beim Lesen der Datei")  # Fehler werfen

    if not ereignisse:
        raise ValueError(
            "Keine Ereignisse in der ausgewählten Datei.")  # Fehler werfen, wenn keine Ereignisse gefunden wurden

    maus_steuerung = mouse.Controller()  # Maus-Controller initialisieren
    tastatur_steuerung = keyboard.Controller()  # Tastatur-Controller initialisieren

    start_zeit = ereignisse[0][1]  # Startzeit des ersten Ereignisses

    for ereignis in ereignisse:
        if esc_flag.is_set() or stop_event.is_set():  # Abbrechen, wenn ESC-Flag oder Stop-Event gesetzt ist
            bool_dauerschleife = False
            break

        ereignis_typ, ereignis_zeit, ereignis_daten = ereignis  # Ereignisdaten extrahieren
        verzögerung = ereignis_zeit - start_zeit  # Verzögerung berechnen
        time.sleep(verzögerung)  # Verzögerung einfügen
        start_zeit = ereignis_zeit  # Startzeit aktualisieren

        try:
            if ereignis_typ == 'klick':
                x, y, taste_name = ereignis_daten
                taste = mouse.Button.left if taste_name == 'left' else mouse.Button.right  # Maustaste bestimmen
                maus_steuerung.position = (x, y)  # Mausposition setzen
                maus_steuerung.click(taste)  # Mausklick ausführen
            elif ereignis_typ == 'tastendruck':
                taste = hole_taste(ereignis_daten)  # Taste verarbeiten
                if taste is not None:
                    tastatur_steuerung.press(taste)  # Taste drücken
            elif ereignis_typ == 'tastenfreigabe':
                taste = hole_taste(ereignis_daten)  # Taste verarbeiten
                if taste is not None:
                    tastatur_steuerung.release(taste)  # Taste freigeben
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Ereignisses {ereignis}: {e}")  # Fehlermeldung ausgeben
            traceback.print_exc()  # Traceback drucken

    if bool_dauerschleife:
        spiele_ereignisse_ab(dateipfad)  # Ereignisse erneut abspielen, wenn Dauerschleife aktiv ist
        time.sleep(10)
    else:
        messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")


# Funktion, die einen Listener für ESC-Tastendrücke startet
def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()  # Startet den Listener und wartet, bis er beendet wird


# Funktion, die auf ESC-Tastendrücke reagiert
def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:  # Überprüft, ob die ESC-Taste gedrückt wurde
        esc_flag.set()  # Setzt das esc_flag-Event
        return False  # Beendet den Listener
