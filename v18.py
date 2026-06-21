import serial
import time
import threading
import sys
from pynput import keyboard

# --- CONFIGURATION ---
PORT_MAC = '/dev/tty.usbmodem21301'
BAUD_RATE = 125000
HB1 = bytes.fromhex("aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad")

# Limites des moteurs et taille du pas (vitesse)
MIN_POS = 0
MAX_POS = 3000
STEP = 25  # Réduit à 50 pour un mouvement plus doux en maintien continu

# État actuel des moteurs (initialisés à 1500, au milieu)
current_positions = {
    1: 1500, # Bras Droit
    2: 1500, # Bras Gauche
    3: 1500, # Buste
    4: 1500  # Tête
}

# Configuration des touches
COMMANDS = {
    'z': ("Tête Gauche", 4, STEP),
    's': ("Tête Droite", 4, -STEP),
    'e': ("Bras G Haut", 2, STEP),
    'd': ("Bras G Bas", 2, -STEP),
    'r': ("Bras D Haut", 1, -STEP),
    'f': ("Bras D Bas", 1, STEP),
    't': ("Buste Gauche", 3, STEP),
    'g': ("Buste Droit", 3, -STEP),
}

# Set contenant les touches actuellement maintenues enfoncées
active_keys = set()
running = True

def build_frame(token, motor_id, position):
    pos_bytes = position.to_bytes(2, byteorder='little')
    payload = bytes.fromhex("14 00 61") + token + bytes.fromhex("03 01") + bytes([motor_id]) + bytes.fromhex("01") + pos_bytes + bytes.fromhex("00 00 00 00 00")
    checksum = 255 - (sum(payload) % 256)
    return bytes.fromhex("aa aa aa") + payload + bytes([checksum])

def keep_alive(ser):
    while running:
        ser.write(HB1)
        time.sleep(2.0)

# --- GESTION DU CLAVIER (PYNPUT) ---
def on_press(key):
    global running
    try:
        if hasattr(key, 'char') and key.char:
            char = key.char.lower()
            if char in COMMANDS or char == '0':
                active_keys.add(char)
            elif char == '!':
                running = False
    except Exception:
        pass

def on_release(key):
    try:
        if hasattr(key, 'char') and key.char:
            char = key.char.lower()
            if char in active_keys:
                active_keys.discard(char)
    except Exception:
        pass

def display_menu():
    print("\n--- EILIK CONTROL MENU (MAINTIEN CONTINU TEMPS RÉEL) ---")
    print("[Z/S] Tête      [E/D] Bras Gauche")
    print("[R/F] Bras Droit[T/G] Buste")
    print("[0] RESET       [!] Quit")
    print("------------------------------------------------------")
    print("Clique sur cette fenêtre de terminal pour piloter Eilik.")

def main():
    global running
    try:
        ser = serial.Serial(PORT_MAC, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Erreur de connexion : {e}")
        return

    ser.rts = False; ser.dtr = True; time.sleep(1)

    ser.reset_input_buffer()
    ser.write(HB1)
    time.sleep(0.3)
    rep = ser.read(ser.in_waiting)
    key = rep[6:11] if len(rep) >= 11 else None

    if not key:
        print("Erreur: Impossible d'obtenir la clé de session d'Eilik.")
        ser.close()
        return

    # Lancement du Heartbeat
    threading.Thread(target=keep_alive, args=(ser,), daemon=True).start()

    # Lancement de l'écouteur de clavier pynput
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    display_menu()

    # Boucle de jeu (Game Loop)
    while running:
        status_msgs = []

        # Reset demandé
        if '0' in active_keys:
            active_keys.discard('0') # On ne le fait qu'une fois
            for motor_id in current_positions.keys():
                current_positions[motor_id] = 1500
                ser.write(build_frame(key, motor_id, 1500))
                time.sleep(0.0125)
            sys.stdout.write("\r\033[K-> Reset complet effectué.")
            sys.stdout.flush()
            continue

        # Application des mouvements continus
        for k in list(active_keys):
            if k in COMMANDS:
                name, motor_id, delta = COMMANDS[k]
                new_pos = current_positions[motor_id] + delta
                new_pos = max(MIN_POS, min(MAX_POS, new_pos))

                if new_pos != current_positions[motor_id]:
                    current_positions[motor_id] = new_pos
                    ser.write(build_frame(key, motor_id, new_pos))
                    status_msgs.append(f"{name}:{new_pos}")

        # Affichage
        if status_msgs:
            sys.stdout.write("\r\033[K-> " + " | ".join(status_msgs))
            sys.stdout.flush()

        # Vitesse de rafraîchissement (0.05s = 20 Hz)
        time.sleep(0.01)

    print("\nDéconnexion d'Eilik...")
    listener.stop()
    ser.close()

if __name__ == "__main__":
    main()
