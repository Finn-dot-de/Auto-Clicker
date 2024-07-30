import time
from pynput import mouse, keyboard
from src.globaly import aufzeichnung, ereignisse_queue
from src.recording import stoppe_aufzeichnung

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
