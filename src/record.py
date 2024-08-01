# Importiert die benötigten Module und Bibliotheken
import time  # Für Zeitstempel und Verzögerungen
import pyautogui  # Zum Simulieren von Maus- und Tastatureingaben
import pygetwindow as gw  # Zum Interagieren mit Fenstern
from pynput import mouse, keyboard  # Zum Erfassen von Maus- und Tastatureingaben
from src.globals import *  # Importiert globale Variablen und Events aus dem globals-Modul
from tkinter import messagebox, filedialog  # Für Nachrichtenboxen und Dateidialoge
import threading  # Für paralleles Ausführen von Threads

# Funktion zum Drücken der Windows+D-Tastenkombination (Minimiert alle Fenster)
def press_windows_d():
    pyautogui.hotkey('win', 'd')

# Funktion, um ein Fenster mit einem bestimmten Titel in den Vordergrund zu bringen
def bring_window_to_foreground(window_title):
    window = gw.getWindowsWithTitle(window_title)  # Sucht das Fenster anhand des Titels
    if window:
        window[0].activate()  # Bringt das Fenster in den Vordergrund

# Funktion, die bei einem Mausklick ausgeführt wird
def bei_klick(x, y, taste, gedrückt):
    if aufzeichnung and gedrückt:  # Wenn die Aufzeichnung läuft und die Maustaste gedrückt wird
        ereignisse_queue.put(('klick', time.time(), (x, y, taste.name)))  # Fügt das Ereignis zur Ereignis-Queue hinzu

# Funktion, die bei einem Tastendruck ausgeführt wird
def bei_tastendruck(taste):
    if globals.aufzeichnung:  # Wenn die Aufzeichnung läuft
        try:
            ereignis_daten = taste.char if taste.char else str(taste)  # Erfasst die gedrückte Taste
            ereignisse_queue.put(('tastendruck', time.time(), ereignis_daten))  # Fügt das Ereignis zur Ereignis-Queue hinzu
        except AttributeError:
            ereignisse_queue.put(('tastendruck', time.time(), str(taste)))  # Falls keine Zeichentaste, als String hinzufügen
        if taste == keyboard.Key.esc:  # Wenn die ESC-Taste gedrückt wird
            stoppe_aufzeichnung()  # Beendet die Aufzeichnung
            return False  # Beendet den Listener

# Funktion, die bei einer Tastenfreigabe ausgeführt wird
def bei_tastenfreigabe(taste):
    if aufzeichnung:  # Wenn die Aufzeichnung läuft
        ereignis_daten = str(taste)  # Erfasst die freigegebene Taste
        ereignisse_queue.put(('tastenfreigabe', time.time(), ereignis_daten))  # Fügt das Ereignis zur Ereignis-Queue hinzu
        if taste == keyboard.Key.esc:  # Wenn die ESC-Taste freigegeben wird
            return False  # Beendet den Listener

# Funktion zum Starten des Maus-Listeners
def starte_maus_listener():
    with mouse.Listener(on_click=bei_klick) as listener:  # Startet den Listener für Mausklicks
        listener.join()  # Wartet, bis der Listener beendet wird

# Funktion zum Starten des Tastatur-Listeners
def starte_tastatur_listener():
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenfreigabe) as listener:  # Startet den Listener für Tastendrücke und -freigaben
        listener.join()  # Wartet, bis der Listener beendet wird

# Funktion zum Starten der Aufzeichnung
def starte_aufzeichnung():
    aufzeichnung = True  # Setzt die Aufzeichnungs-Variable auf True
    ereignisse_queue.queue.clear()  # Löscht die Ereignis-Queue
    press_windows_d()  # Minimiert alle Fenster
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)  # Erstellt einen Thread für den Maus-Listener
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)  # Erstellt einen Thread für den Tastatur-Listener
    maus_thread.start()  # Startet den Maus-Listener-Thread
    tastatur_thread.start()  # Startet den Tastatur-Listener-Thread

# Funktion zum Stoppen der Aufzeichnung
def stoppe_aufzeichnung():
    aufzeichnung = False  # Setzt die Aufzeichnungs-Variable auf False
    stop_event.set()  # Setzt das Stop-Event
    bring_window_to_foreground('Auto-Clicker')  # Bringt das Hauptfenster in den Vordergrund
    print("Aufzeichnung gestoppt.")  # Gibt eine Meldung auf der Konsole aus
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])  # Öffnet einen Dateidialog zum Speichern der Ereignisse
    if dateipfad:
        try:
            with open(dateipfad, 'w') as f:  # Öffnet die Datei zum Schreiben
                while not ereignisse_queue.empty():  # Solange die Ereignis-Queue nicht leer ist
                    ereignis = globals.ereignisse_queue.get()  # Holt das nächste Ereignis aus der Queue
                    if ereignis[0] == 'tastendruck' and ereignis[2] == 'Key.esc':  # Überspringt ESC-Tastendrücke
                        continue
                    if ereignis[0] == 'tastenfreigabe' and ereignis[2] == 'Key.esc':  # Überspringt ESC-Tastenfreigaben
                        continue
                    f.write(f"{ereignis}\n")  # Schreibt das Ereignis in die Datei
            messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")  # Zeigt eine Nachricht an, dass die Ereignisse gespeichert wurden
        except Exception as e:  # Bei Fehlern während des Speicherns
            print(f"Fehler beim Speichern der Datei: {e}")  # Gibt eine Fehlermeldung auf der Konsole aus
