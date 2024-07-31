# main.py

import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
import threading
from record import starte_aufzeichnung, stoppe_aufzeichnung
from replay import spiele_ereignisse_ab
import globals  # Importieren der globalen Variablen
from pynput import mouse, keyboard

def spiele_ereignisse_ab_und_zeige_fehlermeldungen():
    globals.esc_flag.clear()
    globals.stop_event.clear()
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
            if not globals.bool_dauerschleife:
                messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")

    check_threads()

def esc_listener():
    with keyboard.Listener(on_press=bei_esc_druck) as listener:
        listener.join()

def bei_esc_druck(taste):
    if taste == keyboard.Key.esc:
        globals.esc_flag.set()
        return False

def update_dauerschleife():
    globals.bool_dauerschleife = dauerschleife_var.get()
    print(f"Dauerschleife ist {'aktiv' if globals.bool_dauerschleife else 'inaktiv'}")

root = tk.Tk()
root.title("Auto-Clicker")
root.geometry("500x500")
root.configure(bg="#f0f0f0")
root.iconbitmap('./icon.ico')

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
