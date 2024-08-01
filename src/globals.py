# Importiert die benötigten Module
import queue  # Für die Ereignis-Queue
import threading  # Für Threading-Events

# Globale Variablen
ereignisse_queue = queue.Queue()  # Erstellt eine Queue für die Speicherung von Ereignissen
aufzeichnung = False  # Boolean-Variable, die anzeigt, ob eine Aufzeichnung läuft
bool_dauerschleife = False  # Boolean-Variable, die anzeigt, ob die Dauerschleife aktiviert ist
esc_flag = threading.Event()  # Event, das gesetzt wird, wenn die ESC-Taste gedrückt wird, um die Wiedergabe oder Aufzeichnung zu beenden
stop_event = threading.Event()  # Event, das gesetzt wird, um die Aufzeichnung oder Wiedergabe zu stoppen
