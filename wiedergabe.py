import time
from pynput import mouse, keyboard
import ast

# Funktion zum Umwandeln von Tastencodes in tatsächliche Tastencodes
def hole_taste(taste_str):
    """
    Wandelt eine Zeichenkette, die einen Tastencode darstellt, in den entsprechenden
    Tastencode von pynput um.

    Args:
        taste_str (str): Die Zeichenkette, die den Tastencode darstellt (z.B. 'Key.space').

    Returns:
        Tastencode: Der entsprechende Tastencode oder die Zeichenkette selbst, wenn keine Umwandlung möglich ist.
    """
    try:
        if taste_str.startswith('Key.'):
            # Überprüft, ob es sich um eine spezielle Taste handelt
            return keyboard.Key[taste_str.split('.')[1]]
        else:
            # Wenn es keine spezielle Taste ist, gebe den String direkt zurück
            return taste_str
    except KeyError:
        # Falls die Umwandlung fehlschlägt, gebe den ursprünglichen String zurück
        return taste_str

# Funktion zur Wiedergabe der aufgezeichneten Ereignisse
def spiele_ereignisse_ab(dateipfad):
    """
    Liest die Ereignisse aus der angegebenen Datei und führt sie in der aufgezeichneten Reihenfolge aus.

    Args:
        dateipfad (str): Der Pfad zur Datei, die die Ereignisse enthält.

    Raises:
        ValueError: Falls beim Lesen der Datei ein Fehler auftritt oder keine Ereignisse vorhanden sind.
    """
    try:
        # Lese die Datei und konvertiere jede Zeile zurück in ein Python-Objekt
        with open(dateipfad, 'r') as f:
            ereignisse = [ast.literal_eval(line.strip()) for line in f]
    except Exception as e:
        # Fehler beim Lesen der Datei
        raise ValueError(f"Fehler beim Lesen der Datei: {e}")

    # Überprüfe, ob Ereignisse vorhanden sind
    if not ereignisse:
        raise ValueError("Keine Ereignisse in der ausgewählten Datei.")

    # Initialisiere die Controller für Maus und Tastatur
    maus_steuerung = mouse.Controller()
    tastatur_steuerung = keyboard.Controller()

    start_zeit = ereignisse[0][1]  # Speichere den Startzeitpunkt des ersten Ereignisses
    for ereignis in ereignisse:
        ereignis_typ, ereignis_zeit, ereignis_daten = ereignis
        verzögerung = ereignis_zeit - start_zeit  # Berechne die Verzögerung seit dem letzten Ereignis
        time.sleep(verzögerung)  # Warte für die berechnete Verzögerung
        start_zeit = ereignis_zeit  # Aktualisiere den Startzeitpunkt

        # Verarbeite Mausklickereignisse
        if ereignis_typ == 'klick':
            x, y, taste_name = ereignis_daten
            taste = mouse.Button.left if taste_name == 'left' else mouse.Button.right
            maus_steuerung.position = (x, y)  # Setze die Mausposition
            maus_steuerung.click(taste)  # Führe den Mausklick aus

        # Verarbeite Tastendruckereignisse
        elif ereignis_typ == 'tastendruck':
            taste = hole_taste(ereignis_daten)  # Hole den tatsächlichen Tastencode
            try:
                tastatur_steuerung.press(taste)  # Drücke die Taste
            except ValueError:
                # Fehlerbehandlung, falls die Taste nicht gedrückt werden kann
                print(f"Taste '{taste}' kann nicht gedrückt werden")

        # Verarbeite Tastenfreigabeereignisse
        elif ereignis_typ == 'tastenfreigabe':
            taste = hole_taste(ereignis_daten)  # Hole den tatsächlichen Tastencode
            try:
                tastatur_steuerung.release(taste)  # Lasse die Taste los
            except ValueError:
                # Fehlerbehandlung, falls die Taste nicht losgelassen werden kann
                print(f"Taste '{taste}' kann nicht losgelassen werden")
