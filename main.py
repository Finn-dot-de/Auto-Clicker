import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
from src.globaly import bool_dauerschleife
from src.recording import starte_aufzeichnung
from src.playback import spiele_ereignisse_ab

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

wiedergabe_button = tk.Button(rahmen, text="Ereignisse abspielen", command=spiele_ereignisse_ab, width=25, height=2, font=custom_font, bg="#FFC107", fg="white", relief=tk.RAISED, borderwidth=2)
wiedergabe_button.pack(pady=10)

root.mainloop()
