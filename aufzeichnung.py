import time
import threading
from pynput import mouse, keyboard
import tkinter as tk
from tkinter import messagebox

# Globale Variablen für die Aufzeichnung
ereignisse = []  # Liste, um alle erfassten Ereignisse zu speichern
aufzeichnung = False  # Flag, das angibt, ob die Aufzeichnung aktiv ist

# Funktion zum Stoppen der Aufzeichnung und Anzeigen des Pop-ups
def stoppe_aufzeichnung():
    global aufzeichnung
    aufzeichnung = False  # Setze das Flag für die Aufzeichnung auf False
    # Zeige ein Pop-up an, dass die Aufzeichnung beendet wurde
    root = tk.Tk()
    root.withdraw()  # Verstecke das Hauptfenster
    messagebox.showinfo("Information", "Aufzeichnung erfolgreich beendet.")
    root.destroy()  # Schließe das Tkinter-Fenster

# Funktion, die bei einem Mausklick aufgerufen wird
def bei_klick(x, y, taste, gedrückt):
    global aufzeichnung
    if aufzeichnung:
        if gedrückt:
            # Wenn die Aufzeichnung aktiv ist und die Maustaste gedrückt wurde,
            # speichern wir die Klick-Informationen in der Ereignisliste
            print(f"Mausklick bei ({x}, {y}) mit {taste.name}")
            ereignisse.append(('klick', time.time(), (x, y, taste.name)))

# Funktion, die bei einem Tastendruck aufgerufen wird
def bei_tastendruck(taste):
    global aufzeichnung
    if aufzeichnung:
        try:
            # Versuche, die gedrückte Taste zu erfassen und zu speichern
            print(f"Taste {taste.char} gedrückt")
            ereignisse.append(('tastendruck', time.time(), taste.char))
        except AttributeError:
            # Falls die Taste keine Zeichen-Darstellung hat (z.B. Funktionstasten),
            # speichern wir den Typ der Taste als String
            print(f"Spezialtaste {taste} gedrückt")
            ereignisse.append(('tastendruck', time.time(), str(taste)))
        # Überprüfen, ob die ESC-Taste gedrückt wurde, um die Aufzeichnung zu beenden
        if taste == keyboard.Key.esc:
            print("ESC-Taste gedrückt. Aufzeichnung wird gestoppt.")
            stoppe_aufzeichnung()  # Stoppe die Aufzeichnung und zeige das Pop-up
            return False  # Beende den Listener

# Funktion, die bei einer Tastenfreigabe aufgerufen wird
def bei_tastenfreigabe(taste):
    global aufzeichnung
    if aufzeichnung:
        # Wenn die Aufzeichnung aktiv ist und eine Taste losgelassen wurde,
        # speichern wir die Freigabe-Informationen in der Ereignisliste
        print(f"Taste {taste} losgelassen")
        ereignisse.append(('tastenfreigabe', time.time(), str(taste)))
        # Überprüfen, ob die ESC-Taste losgelassen wurde, um die Aufzeichnung zu beenden
        if taste == keyboard.Key.esc:
            return False  # Beende den Listener

# Funktion zum Starten des Maus-Listeners
def starte_maus_listener():
    # Erzeuge einen Maus-Listener, der die `bei_klick` Funktion aufruft
    with mouse.Listener(on_click=bei_klick) as listener:
        listener.join()  # Warte, bis der Listener stoppt

# Funktion zum Starten des Tastatur-Listeners
def starte_tastatur_listener():
    # Erzeuge einen Tastatur-Listener, der die `bei_tastendruck` und `bei_tastenfreigabe` Funktionen aufruft
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenfreigabe) as listener:
        listener.join()  # Warte, bis der Listener stoppt

# Funktion zum Starten der Aufzeichnung
def starte_aufzeichnung():
    global aufzeichnung
    aufzeichnung = True  # Setze das Flag für die Aufzeichnung auf True
    ereignisse.clear()  # Leere die Liste der Ereignisse
    # Erzeuge und starte separate Threads für Maus- und Tastatur-Listener
    maus_thread = threading.Thread(target=starte_maus_listener)
    tastatur_thread = threading.Thread(target=starte_tastatur_listener)
    maus_thread.start()  # Starte den Maus-Listener-Thread
    tastatur_thread.start()  # Starte den Tastatur-Listener-Thread
