import time
import ast
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import font as tkfont
from pynput import mouse, keyboard
import threading
import queue
import traceback

# Globale Variablen
ereignisse_queue = queue.Queue()
aufzeichnung = False
bool_dauerschleife = False
esc_flag = threading.Event()
stop_event = threading.Event()

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
    maus_thread = threading.Thread(target=starte_maus_listener, daemon=True)
    tastatur_thread = threading.Thread(target=starte_tastatur_listener, daemon=True)
    maus_thread.start()
    tastatur_thread.start()

def stoppe_aufzeichnung():
    global aufzeichnung
    aufzeichnung = False
    stop_event.set()
    print("Aufzeichnung gestoppt.")
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if dateipfad:
        try:
            with open(dateipfad, 'w') as f:
                while not ereignisse_queue.empty():
                    ereignis = ereignisse_queue.get()
                    # Filtert ESC-Ereignisse heraus
                    if ereignis[0] == 'tastendruck' and ereignis[2] == 'Key.esc':
                        continue
                    if ereignis[0] == 'tastenfreigabe' and ereignis[2] == 'Key.esc':
                        continue
                    f.write(f"{ereignis}\n")
            messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")
            traceback.print_exc()

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

    if bool_dauerschleife:
        spiele_ereignisse_ab(dateipfad)

def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()

def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:
        esc_flag.set()
        return False

def spiele_ereignisse_ab_und_zeige_fehlermeldungen():
    global bool_dauerschleife
    esc_flag.clear()
    stop_event.clear()
    dateipfad = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if not dateipfad:
        return

    abspielen_thread = threading.Thread(target=spiele_ereignisse_ab, args=(dateipfad,), daemon=True)
    esc_thread = threading.Thread(target=esc_listener, daemon=True)

    abspielen_thread.start()
    esc_thread.start()

    def check_threads():
        if abspielen_thread.is_alive() or esc_thread.is_alive():
            root.after(100, check_threads)
        else:
            if not bool_dauerschleife:
                messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")

    check_threads()

def stoppe_aufzeichnung_und_zeige_benachrichtigung():
    stoppe_aufzeichnung()
    messagebox.showinfo("Information", "Aufzeichnung erfolgreich beendet!")

def update_dauerschleife():
    global bool_dauerschleife
    bool_dauerschleife = dauerschleife_var.get()
    print(f"Dauerschleife ist {'aktiv' if bool_dauerschleife else 'inaktiv'}")

root = tk.Tk()
root.title("Auto-Clicker")
root.geometry("500x500")
root.configure(bg="#f0f0f0")

custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

rahmen = tk.Frame(root, bg="#e0e0e0", padx=20, pady=20)
rahmen.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

überschrift = tk.Label(rahmen, text="Auto-Clicker", font=("Helvetica", 16, "bold"), bg="#e0e0e0")
überschrift.pack(pady=10)

start_button = tk.Button(rahmen, text="Aufzeichnung starten", command=starte_aufzeichnung, width=25, height=2, font=custom_font, bg="#4CAF50", fg="white", relief=tk.RAISED, borderwidth=2)
start_button.pack(pady=10)

stop_label = tk.Label(rahmen, text="Drücke ESC zum Beenden der Aufzeichnung\n oder der Dauerschleife", font=("Helvetica", 12), bg="#e0e0e0")
stop_label.pack(pady=10)

dauerschleife_var = tk.BooleanVar()
dauerschleife_checkbox = tk.Checkbutton(rahmen, text="Dauerschleife", variable=dauerschleife_var, onvalue=True, offvalue=False, command=update_dauerschleife, font=("Helvetica", 12), bg="#e0e0e0")
dauerschleife_checkbox.pack(pady=10)

wiedergabe_button = tk.Button(rahmen, text="Ereignisse abspielen", command=spiele_ereignisse_ab_und_zeige_fehlermeldungen, width=25, height=2, font=custom_font, bg="#FFC107", fg="white", relief=tk.RAISED, borderwidth=2)
wiedergabe_button.pack(pady=10)

root.mainloop()
