# Importiert die benötigten Module und Bibliotheken
import time  # Zum Arbeiten mit Zeitfunktionen
import ast  # Zum sicheren Parsen von Python-Ausdrücken aus Strings
import traceback  # Zum Drucken von Tracebacks bei Ausnahmen
from pynput import mouse, keyboard  # Zum Erfassen und Steuern von Maus- und Tastaturereignissen
from src.globals import *  # Importiert globale Variablen aus dem globals-Modul
from tkinter import messagebox  # Zum Anzeigen von Popup-Nachrichten

# Funktion zum Konvertieren von Tastenzeichenfolgen in Tastenobjekte
def hole_taste(taste_str):
    print(f"Verarbeite Tastencode: {taste_str}")  # Debug-Ausgabe zur Überwachung der Tastencodes

    # Behandelt spezielle Tasten, die mit 'Key.' beginnen
    if taste_str.startswith('Key.'):
        try:
            # Versucht, die entsprechende Taste aus dem keyboard.Key-Objekt zu holen
            return getattr(keyboard.Key, taste_str.split('.')[1])
        except AttributeError:
            print(f"Unbekannter Tastencode: {taste_str}")  # Gibt eine Fehlermeldung aus, wenn die Taste nicht gefunden wird
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
    global bool_dauerschleife  # Verwendet die globale Variable bool_dauerschleife
    try:
        # Öffnet die Datei und liest die Ereignisse
        with open(dateipfad, 'r') as f:
            ereignisse = [ast.literal_eval(line.strip()) for line in f]
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")  # Gibt eine Fehlermeldung aus, wenn die Datei nicht gelesen werden kann
        traceback.print_exc()  # Druckt den vollständigen Fehler-Traceback
        raise ValueError("Fehler beim Lesen der Datei")

    if not ereignisse:
        raise ValueError("Keine Ereignisse in der ausgewählten Datei.")  # Hebt einen Fehler hervor, wenn keine Ereignisse gefunden werden

    # Erstellt Controller-Objekte für Maus und Tastatur
    maus_steuerung = mouse.Controller()
    tastatur_steuerung = keyboard.Controller()

    start_zeit = ereignisse[0][1]  # Speichert die Startzeit des ersten Ereignisses

    # Beginnt die Dauerschleife, wenn aktiviert
    while True:
        # Überprüft, ob ESC gedrückt wurde oder das Stop-Event gesetzt ist
        if esc_flag.is_set() or stop_event.is_set():
            bool_dauerschleife = False  # Setzt die Dauerschleife-Variable auf False
            break

        # Durchläuft alle Ereignisse in der Liste
        for ereignis in ereignisse:
            if esc_flag.is_set() or stop_event.is_set():  # Überprüft erneut, ob ESC gedrückt wurde oder das Stop-Event gesetzt ist
                bool_dauerschleife = False  # Setzt die Dauerschleife-Variable auf False
                break

            # Extrahiert die Ereignisdaten
            ereignis_typ, ereignis_zeit, ereignis_daten = ereignis
            verzögerung = ereignis_zeit - start_zeit  # Berechnet die Verzögerung basierend auf der Zeit des Ereignisses
            time.sleep(verzögerung)  # Wartet für die berechnete Verzögerungszeit
            start_zeit = ereignis_zeit  # Aktualisiert die Startzeit

            try:
                # Verarbeitet Klick-Ereignisse
                if ereignis_typ == 'klick':
                    x, y, taste_name = ereignis_daten  # Extrahiert die Klick-Daten
                    taste = mouse.Button.left if taste_name == 'left' else mouse.Button.right  # Bestimmt die Maustaste
                    maus_steuerung.position = (x, y)  # Setzt die Mausposition
                    maus_steuerung.click(taste)  # Führt den Klick aus
                # Verarbeitet Tastendruck-Ereignisse
                elif ereignis_typ == 'tastendruck':
                    taste = hole_taste(ereignis_daten)  # Konvertiert den Tastencode in ein Tastenobjekt
                    if taste is not None:
                        tastatur_steuerung.press(taste)  # Drückt die Taste
                # Verarbeitet Tastenfreigabe-Ereignisse
                elif ereignis_typ == 'tastenfreigabe':
                    taste = hole_taste(ereignis_daten)  # Konvertiert den Tastencode in ein Tastenobjekt
                    if taste is not None:
                        tastatur_steuerung.release(taste)  # Lässt die Taste los
            except Exception as e:
                print(f"Fehler beim Verarbeiten des Ereignisses {ereignis}: {e}")  # Gibt eine Fehlermeldung aus, wenn ein Fehler auftritt
                traceback.print_exc()  # Druckt den vollständigen Fehler-Traceback

        if not bool_dauerschleife:  # Bricht die Schleife ab, wenn die Dauerschleife deaktiviert ist
            # Zeigt ein Popup für das Ende des Replays an
            messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")
            break
        elif bool_dauerschleife:
            spiele_ereignisse_ab(dateipfad)

# Funktion, die einen Listener für ESC-Tastendrücke startet
def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()  # Startet den Listener und wartet, bis er beendet wird

# Funktion, die auf ESC-Tastendrücke reagiert
def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:  # Überprüft, ob die ESC-Taste gedrückt wurde
        esc_flag.set()  # Setzt das esc_flag-Event
        return False  # Beendet den Listener
