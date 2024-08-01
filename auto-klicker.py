# Importieren der benötigten Module und Bibliotheken
import time  # Zum Arbeiten mit Zeitfunktionen
import ast  # Zum sicheren Parsen von Strings in Python-Objekte
import tkinter as tk  # GUI-Bibliothek für das Erstellen von grafischen Benutzeroberflächen
from tkinter import messagebox, filedialog  # Importieren von Dialogboxen und Dateiauswahl-Dialogen aus tkinter
from tkinter import font as tkfont  # Importieren des Font-Moduls aus tkinter
from pynput import mouse, keyboard  # Bibliothek zum Überwachen von Maus- und Tastatureingaben
import threading  # Modul zum Erstellen und Verwalten von Threads
import queue  # Modul für Warteschlangen (Queues)
import traceback  # Modul zum Drucken von Tracebacks für Fehler
import pyautogui  # Modul zur Automatisierung von GUI-Interaktionen
import pygetwindow as gw  # Modul zum Arbeiten mit Fenstern auf dem Desktop

###################################################################################################################

# Pfad zu .ico-Icon
ICON_PATH = './icon.ico'

###################################################################################################################

# Globale Variablen
ereignisse_queue = queue.Queue()  # Warteschlange für Ereignisse
aufzeichnung = False  # Flag zum Starten und Stoppen der Aufzeichnung
bool_dauerschleife = False  # Flag für Dauerschleife
esc_flag = threading.Event()  # Event zum Setzen eines ESC-Flags
stop_event = threading.Event()  # Event zum Stoppen der Aufzeichnung

###################################################################################################################

# Funktion zum Drücken der Windows+D-Taste (zeigt Desktop an)
def press_windows_d():
    pyautogui.hotkey('win', 'd')

# Funktion zum Hervorheben eines Fensters anhand seines Titels
def bring_window_to_foreground(window_title):
    window = gw.getWindowsWithTitle(window_title)  # Fenster mit bestimmtem Titel finden
    if window:
        window[0].activate()  # Das erste gefundene Fenster aktivieren

###################################################################################################################

# Funktion, die bei einem Mausklick ausgeführt wird
def bei_klick(x, y, taste, gedrückt):
    if aufzeichnung and gedrückt:  # Nur bei aktiver Aufzeichnung und gedrückter Taste
        ereignisse_queue.put(('klick', time.time(), (x, y, taste.name)))  # Ereignis in die Warteschlange stellen

# Funktion, die bei einem Tastendruck ausgeführt wird
def bei_tastendruck(taste):
    if aufzeichnung:  # Nur bei aktiver Aufzeichnung
        try:
            ereignis_daten = taste.char if taste.char else str(taste)  # Zeichen oder Taste als String
            ereignisse_queue.put(('tastendruck', time.time(), ereignis_daten))  # Ereignis in die Warteschlange stellen
        except AttributeError:
            ereignisse_queue.put(('tastendruck', time.time(), str(taste)))  # Fallback bei Fehler
        if taste == keyboard.Key.esc:  # Bei ESC-Taste
            stoppe_aufzeichnung()  # Aufzeichnung stoppen
            return False

# Funktion, die bei einer Tastenfreigabe ausgeführt wird
def bei_tastenfreigabe(taste):
    if aufzeichnung:  # Nur bei aktiver Aufzeichnung
        ereignis_daten = str(taste)  # Taste als String
        ereignisse_queue.put(('tastenfreigabe', time.time(), ereignis_daten))  # Ereignis in die Warteschlange stellen
        if taste == keyboard.Key.esc:  # Bei ESC-Taste
            return False

###################################################################################################################

# Funktion zum Starten des Maus-Listeners
def starte_maus_listener():
    with mouse.Listener(on_click=bei_klick) as listener:  # Listener für Mausklicks
        listener.join()  # Warten bis der Listener beendet wird

# Funktion zum Starten des Tastatur-Listeners
def starte_tastatur_listener():
    with keyboard.Listener(on_press=bei_tastendruck, on_release=bei_tastenfreigabe) as listener:  # Listener für Tastendrucke und -freigaben
        listener.join()  # Warten bis der Listener beendet wird

###################################################################################################################

# Funktion zum Starten der Aufzeichnung
def starte_aufzeichnung():
    global aufzeichnung  # Zugriff auf die globale Variable
    aufzeichnung = True  # Aufzeichnung starten
    ereignisse_queue.queue.clear()  # Warteschlange leeren
    press_windows_d()  # Desktop anzeigen
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)  # Thread für Maus-Listener
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)  # Thread für Tastatur-Listener
    maus_thread.start()  # Thread starten
    tastatur_thread.start()  # Thread starten

# Funktion zum Stoppen der Aufzeichnung
def stoppe_aufzeichnung():
    global aufzeichnung  # Zugriff auf die globale Variable
    aufzeichnung = False  # Aufzeichnung stoppen
    stop_event.set()  # Stop-Event setzen
    bring_window_to_foreground('Auto-Clicker')  # Fenster in den Vordergrund bringen
    print("Aufzeichnung gestoppt.")
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])  # Dialog zum Speichern der Datei
    if dateipfad:
        try:
            with open(dateipfad, 'w') as f:  # Datei zum Schreiben öffnen
                while not ereignisse_queue.empty():  # Solange die Warteschlange nicht leer ist
                    ereignis = ereignisse_queue.get()  # Ereignis aus der Warteschlange holen
                    # Filtert ESC-Ereignisse heraus
                    if ereignis[0] == 'tastendruck' and ereignis[2] == 'Key.esc':
                        continue
                    if ereignis[0] == 'tastenfreigabe' and ereignis[2] == 'Key.esc':
                        continue
                    f.write(f"{ereignis}\n")  # Ereignis in die Datei schreiben
            messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")  # Erfolgsnachricht anzeigen
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")  # Fehlermeldung ausgeben
            traceback.print_exc()  # Traceback drucken

###################################################################################################################

# Funktion zum Verarbeiten eines Tastencodes
def hole_taste(taste_str):
    print(f"Verarbeite Tastencode: {taste_str}")  # Debug-Ausgabe

    # Handle spezielle Tasten
    if taste_str.startswith('Key.'):
        try:
            return getattr(keyboard.Key, taste_str.split('.')[1])  # Rückgabe der entsprechenden Taste
        except AttributeError:
            print(f"Unbekannter Tastencode: {taste_str}")  # Fehlermeldung bei unbekanntem Tastencode
            return None

    # Handle druckbare Zeichen
    elif len(taste_str) == 1 and taste_str.isprintable():
        return keyboard.KeyCode(char=taste_str)  # Rückgabe des Zeichens als KeyCode

    # Handle Maustasten
    elif taste_str in ['left', 'right', 'middle']:
        return getattr(mouse.Button, taste_str)  # Rückgabe der entsprechenden Maustaste

    # Unbekannte Tasten oder Zeichen
    else:
        print(f"Unbekannter Tastencode: {taste_str}")  # Fehlermeldung bei unbekanntem Tastencode
        return None

# Funktion zum Abspielen der aufgezeichneten Ereignisse
def spiele_ereignisse_ab(dateipfad):
    global bool_dauerschleife
    try:
        with open(dateipfad, 'r') as f:  # Datei zum Lesen öffnen
            ereignisse = [ast.literal_eval(line.strip()) for line in f]  # Ereignisse aus der Datei lesen und parsen
    except Exception as e:
        print(f"Fehler beim Lesen der Datei: {e}")  # Fehlermeldung ausgeben
        traceback.print_exc()  # Traceback drucken
        raise ValueError("Fehler beim Lesen der Datei")  # Fehler werfen

    if not ereignisse:
        raise ValueError("Keine Ereignisse in der ausgewählten Datei.")  # Fehler werfen, wenn keine Ereignisse gefunden wurden

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

###################################################################################################################

# Funktion zum Starten eines ESC-Listeners
def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:  # Listener für ESC-Tastendruck
        listener.join()  # Warten bis der Listener beendet wird

# Funktion, die bei einem ESC-Tastendruck ausgeführt wird
def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:  # Bei ESC-Taste
        esc_flag.set()  # ESC-Flag setzen
        return False

###################################################################################################################

# Funktion zum Abspielen der Ereignisse und Anzeigen von Fehlermeldungen
def spiele_ereignisse_ab_und_zeige_fehlermeldungen():
    global bool_dauerschleife
    esc_flag.clear()  # ESC-Flag zurücksetzen
    stop_event.clear()  # Stop-Event zurücksetzen
    dateipfad = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])  # Dialog zum Öffnen der Datei
    if not dateipfad:
        return

    abspielen_thread = threading.Thread(target=spiele_ereignisse_ab, args=(dateipfad,), daemon=True)  # Thread zum Abspielen der Ereignisse
    esc_thread = threading.Thread(target=esc_listener, daemon=True)  # Thread zum Starten des ESC-Listeners

    abspielen_thread.start()  # Thread starten
    esc_thread.start()  # Thread starten

    def check_threads():
        if abspielen_thread.is_alive() or esc_thread.is_alive():  # Überprüfen, ob Threads noch laufen
            root.after(100, check_threads)  # Erneut nach 100ms überprüfen
        else:
            if not bool_dauerschleife:
                messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")  # Erfolgsnachricht anzeigen

    check_threads()  # Threads überprüfen

###################################################################################################################

# Funktion zum Stoppen der Aufzeichnung und Anzeigen einer Benachrichtigung
def stoppe_aufzeichnung_und_zeige_benachrichtigung():
    stoppe_aufzeichnung()  # Aufzeichnung stoppen
    messagebox.showinfo("Information", "Aufzeichnung erfolgreich beendet!")  # Erfolgsnachricht anzeigen

# Funktion zum Aktualisieren der Dauerschleifen-Variable
def update_dauerschleife():
    global bool_dauerschleife
    bool_dauerschleife = dauerschleife_var.get()  # Wert der Dauerschleifen-Checkbox lesen
    print(f"Dauerschleife ist {'aktiv' if bool_dauerschleife else 'inaktiv'}")  # Debug-Ausgabe

###################################################################################################################

# Erstellen des Hauptfensters der Anwendung
root = tk.Tk()
root.title("Auto-Clicker")  # Titel des Fensters setzen
root.geometry("500x500")  # Größe des Fensters setzen
root.configure(bg="#f0f0f0")  # Hintergrundfarbe setzen
root.iconbitmap(ICON_PATH)  # Icon setzen

# Erstellen einer benutzerdefinierten Schriftart
custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

# Erstellen eines Rahmens im Hauptfenster
rahmen = tk.Frame(root, bg="#e0e0e0", padx=20, pady=20)
rahmen.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Erstellen und Platzieren einer Überschrift im Rahmen
überschrift = tk.Label(rahmen, text="Auto-Clicker", font=("Helvetica", 16, "bold"), bg="#e0e0e0")
überschrift.pack(pady=10)

# Erstellen und Platzieren eines Start-Buttons im Rahmen
start_button = tk.Button(rahmen, text="Aufzeichnung starten", command=starte_aufzeichnung, width=25, height=2, font=custom_font, bg="#4CAF50", fg="white", relief=tk.RAISED, borderwidth=2)
start_button.pack(pady=10)

# Erstellen und Platzieren eines Labels zur Information über das Beenden der Aufzeichnung im Rahmen
stop_label = tk.Label(rahmen, text="Drücke ESC zum Beenden der Aufzeichnung\n oder der Dauerschleife", font=("Helvetica", 12), bg="#e0e0e0")
stop_label.pack(pady=10)

# Erstellen und Platzieren einer Checkbox für die Dauerschleife im Rahmen
dauerschleife_var = tk.BooleanVar()
dauerschleife_checkbox = tk.Checkbutton(rahmen, text="Dauerschleife", variable=dauerschleife_var, onvalue=True, offvalue=False, command=update_dauerschleife, font=("Helvetica", 12), bg="#e0e0e0")
dauerschleife_checkbox.pack(pady=10)

# Erstellen und Platzieren eines Wiedergabe-Buttons im Rahmen
wiedergabe_button = tk.Button(rahmen, text="Ereignisse abspielen", command=spiele_ereignisse_ab_und_zeige_fehlermeldungen, width=25, height=2, font=custom_font, bg="#FFC107", fg="white", relief=tk.RAISED, borderwidth=2)
wiedergabe_button.pack(pady=10)

###################################################################################################################

# Starten der Haupt-Ereignisschleife der Anwendung
root.mainloop()

###################################################################################################################
