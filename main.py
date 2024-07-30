import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import font as tkfont
from aufzeichnung import starte_aufzeichnung, ereignisse
from wiedergabe import spiele_ereignisse_ab

# Funktion zum Speichern der Ereignisse in einer Datei
def speichere_ereignisse():
    dateipfad = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if dateipfad:
        with open(dateipfad, 'w') as f:
            for ereignis in ereignisse:
                f.write(f"{ereignis}\n")
        messagebox.showinfo("Information", f"Ereignisse gespeichert in {dateipfad}")

# Funktion zum Abspielen der Ereignisse und zur Fehlerbehandlung
def spiele_ereignisse_ab_und_zeige_fehlermeldungen():
    dateipfad = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Textdateien", "*.txt")])
    if not dateipfad:
        return

    try:
        spiele_ereignisse_ab(dateipfad)
        messagebox.showinfo("Information", "Wiedergabe erfolgreich abgeschlossen!")
    except ValueError as e:
        messagebox.showerror("Fehler", str(e))

# Erstellen der GUI mit Tkinter
root = tk.Tk()
root.title("Ereignis-Rekorder und -Wiedergabe")  # Fenstertitel
root.geometry("500x460")  # Fenstergröße
root.configure(bg="#f0f0f0")  # Hintergrundfarbe

# Definieren eines benutzerdefinierten Schriftstils
custom_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

# Rahmen für die Schaltflächen
rahmen = tk.Frame(root, bg="#e0e0e0", padx=20, pady=20)
rahmen.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Überschrift
überschrift = tk.Label(rahmen, text="Ereignis-Rekorder und -Wiedergabe", font=("Helvetica", 16, "bold"), bg="#e0e0e0")
überschrift.pack(pady=10)

# Schaltfläche zum Starten der Aufzeichnung
start_button = tk.Button(rahmen, text="Aufzeichnung starten", command=starte_aufzeichnung, width=25, height=2, font=custom_font, bg="#4CAF50", fg="white", relief=tk.RAISED, borderwidth=2)
start_button.pack(pady=10)

# Label für das Beenden der Aufzeichnung
stop_label = tk.Label(rahmen, text="Drücke ESC zum Beenden der Aufzeichnung", font=("Helvetica", 12), bg="#e0e0e0")
stop_label.pack(pady=10)

# Schaltfläche zum Speichern der Ereignisse
speichern_button = tk.Button(rahmen, text="Ereignisse speichern", command=speichere_ereignisse, width=25, height=2, font=custom_font, bg="#2196F3", fg="white", relief=tk.RAISED, borderwidth=2)
speichern_button.pack(pady=10)

# Schaltfläche zum Abspielen der Ereignisse
wiedergabe_button = tk.Button(rahmen, text="Ereignisse abspielen", command=spiele_ereignisse_ab_und_zeige_fehlermeldungen, width=25, height=2, font=custom_font, bg="#FFC107", fg="white", relief=tk.RAISED, borderwidth=2)
wiedergabe_button.pack(pady=10)

# Informationen über das Programm
info_label = tk.Label(rahmen, text="Wählen Sie eine der folgenden Optionen aus:", font=("Helvetica", 10), bg="#e0e0e0")
info_label.pack(pady=10)

# Starten der Hauptschleife der GUI
root.mainloop()
