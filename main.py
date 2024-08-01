# Importiert die benötigten Module und Bibliotheken
import tkinter as tk  # Für die Erstellung der GUI
from tkinter import filedialog, messagebox, font as tkfont  # Für Dateidialoge, Nachrichtenboxen und Schriftarten
import threading  # Für paralleles Ausführen von Threads
from src.globals import *  # Importiert globale Variablen aus dem globals-Modul
from src.record import starte_aufzeichnung  # Importiert die Funktion zum Starten der Aufzeichnung
from src.replay import spiele_ereignisse_ab  # Importiert die Funktion zum Abspielen der Ereignisse
from pynput import keyboard  # Zum Erfassen von Tastatureingaben
import os

# Funktion zum Abspielen der Ereignisse und Anzeigen von Fehlermeldungen
def spiele_ereignisse_ab_und_zeige_fehlermeldungen():
    esc_flag.clear()  # Setzt das ESC-Flag zurück
    stop_event.clear()  # Setzt das Stop-Event zurück
    dateipfad = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])  # Öffnet einen Dateidialog zur Auswahl der Datei
    if not dateipfad:
        return  # Bricht ab, wenn keine Datei ausgewählt wurde

    # Erstellt und startet einen Thread zum Abspielen der Ereignisse
    abspielen_thread = threading.Thread(target=spiele_ereignisse_ab, args=(dateipfad,), daemon=True)
    esc_thread = threading.Thread(target=esc_listener, daemon=True)

    abspielen_thread.start()  # Startet den Abspiel-Thread
    esc_thread.start()  # Startet den ESC-Listener-Thread

    # Funktion zur Überprüfung der Threads
    def check_threads():
        if abspielen_thread.is_alive() or esc_thread.is_alive():  # Überprüft, ob die Threads noch laufen
            root.after(100, check_threads)  # Überprüft nach 100ms erneut
        else:
            if not bool_dauerschleife:  # Zeigt eine Nachricht an, wenn die Dauerschleife nicht aktiviert ist
                messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")

    check_threads()  # Startet die Überprüfung der Threads

# Funktion, die einen Listener für ESC-Tastendrücke startet
def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()  # Startet den Listener und wartet, bis er beendet wird

# Funktion, die auf ESC-Tastendrücke reagiert
def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:  # Überprüft, ob die ESC-Taste gedrückt wurde
        esc_flag.set()  # Setzt das esc_flag-Event
        return False  # Beendet den Listener

# Funktion zur Aktualisierung der Dauerschleifen-Variable
def update_dauerschleife():
    global bool_dauerschleife  # Deklariert die Variable als global
    bool_dauerschleife = dauerschleife_var.get()  # Aktualisiert die globale Dauerschleifen-Variable
    os.environ['BOOL_DAUERSCHLEIFE'] = str(bool_dauerschleife)
    print(f"Dauerschleife ist {'aktiv' if bool_dauerschleife else 'inaktiv'}")  # Gibt den Status der Dauerschleife aus
    test = os.environ['BOOL_DAUERSCHLEIFE'] = str(bool_dauerschleife)
    print("main.py<<<<<<<<<<<<<",test)

# Erstellt das Hauptfenster der Anwendung
root = tk.Tk()
root.title("Auto-Clicker")  # Setzt den Titel des Fensters
root.geometry("500x500")  # Setzt die Größe des Fensters
root.configure(bg="#f0f0f0")  # Setzt den Hintergrund des Fensters
root.iconbitmap('./icon.ico')  # Setzt das Icon des Fensters

# Erstellt eine benutzerdefinierte Schriftart
custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

# Erstellt einen Rahmen zur Gruppierung von Widgets
rahmen = tk.Frame(root, bg="#e0e0e0", padx=20, pady=20)
rahmen.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Erstellt und platziert eine Überschrift
überschrift = tk.Label(rahmen, text="Auto-Clicker", font=("Helvetica", 16, "bold"), bg="#e0e0e0")
überschrift.pack(pady=10)

# Erstellt und platziert einen Start-Button zur Aufzeichnung
start_button = tk.Button(rahmen, text="Aufzeichnung starten", command=starte_aufzeichnung, width=25, height=2, font=custom_font, bg="#4CAF50", fg="white", relief=tk.RAISED, borderwidth=2)
start_button.pack(pady=10)

# Erstellt und platziert ein Label mit einer Anleitung
stop_label = tk.Label(rahmen, text="Drücke ESC zum Beenden der Aufzeichnung\n oder der Dauerschleife", font=("Helvetica", 12), bg="#e0e0e0")
stop_label.pack(pady=10)

# Erstellt und platziert eine Checkbox für die Dauerschleifen-Option
dauerschleife_var = tk.BooleanVar()  # Erstellt eine Variable für die Checkbox
dauerschleife_checkbox = tk.Checkbutton(rahmen, text="Dauerschleife", variable=dauerschleife_var, onvalue=True, offvalue=False, command=update_dauerschleife, font=("Helvetica", 12), bg="#e0e0e0")
dauerschleife_checkbox.pack(pady=10)

# Erstellt und platziert einen Button zum Abspielen der Ereignisse
wiedergabe_button = tk.Button(rahmen, text="Ereignisse abspielen", command=spiele_ereignisse_ab_und_zeige_fehlermeldungen, width=25, height=2, font=custom_font, bg="#FFC107", fg="white", relief=tk.RAISED, borderwidth=2)
wiedergabe_button.pack(pady=10)

# Startet die Hauptschleife der Anwendung
root.mainloop()