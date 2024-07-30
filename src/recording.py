import threading
from tkinter import messagebox, filedialog
from src.listeners import bei_klick, bei_tastendruck, bei_tastenfreigabe
from src.globaly import aufzeichnung, ereignisse_queue, stop_event
from pynput import mouse, keyboard
import traceback

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
