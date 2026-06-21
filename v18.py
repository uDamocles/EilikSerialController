import serial
import time
import threading
import sys
from pynput import keyboard

# --- CONFIGURATION ---
PORT_MAC = '/dev/tty.usbmodem21301'
BAUD_RATE = 125000
HB1 = bytes.fromhex("aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad")

# Motor limits and step size (speed)
MIN_POS = 0
MAX_POS = 3000
STEP = 25  # Reduced to 25 for smoother continuous movement

# Current motor positions (initialized at 1500, the center point)
current_positions = {
    1: 1500, # Right Arm
    2: 1500, # Left Arm
    3: 1500, # Torso
    4: 1500  # Head
}

# Key configuration
COMMANDS = {
    'z': ("Head Left", 4, STEP),
    's': ("Head Right", 4, -STEP),
    'e': ("Left Arm Up", 2, STEP),
    'd': ("Left Arm Down", 2, -STEP),
    'r': ("Right Arm Up", 1, -STEP),
    'f': ("Right Arm Down", 1, STEP),
    't': ("Torso Left", 3, STEP),
    'g': ("Torso Right", 3, -STEP),
}

# Set containing currently held keys
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

# --- KEYBOARD MANAGEMENT (PYNPUT) ---
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
    print("\n--- EILIK CONTROL MENU (REAL-TIME CONTINUOUS HOLD) ---")
    print("[Z/S] Head        [E/D] Left Arm")
    print("[R/F] Right Arm   [T/G] Torso")
    print("[0] RESET         [!] Quit")
    print("------------------------------------------------------")
    print("Click on this terminal window to pilot Eilik.")

def main():
    global running
    try:
        ser = serial.Serial(PORT_MAC, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Connection error: {e}")
        return

    ser.rts = False; ser.dtr = True; time.sleep(1)

    ser.reset_input_buffer()
    ser.write(HB1)
    time.sleep(0.3)
    rep = ser.read(ser.in_waiting)
    key = rep[6:11] if len(rep) >= 11 else None

    if not key:
        print("Error: Could not obtain Eilik session key.")
        ser.close()
        return

    # Start Heartbeat
    threading.Thread(target=keep_alive, args=(ser,), daemon=True).start()

    # Start pynput keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    display_menu()

    # Game Loop
    while running:
        status_msgs = []

        # Reset requested
        if '0' in active_keys:
            active_keys.discard('0') # Only perform once
            for motor_id in current_positions.keys():
                current_positions[motor_id] = 1500
                ser.write(build_frame(key, motor_id, 1500))
                time.sleep(0.0125)
            sys.stdout.write("\r\033[K-> Full reset performed.")
            sys.stdout.flush()
            continue

        # Apply continuous movements
        for k in list(active_keys):
            if k in COMMANDS:
                name, motor_id, delta = COMMANDS[k]
                new_pos = current_positions[motor_id] + delta
                new_pos = max(MIN_POS, min(MAX_POS, new_pos))

                if new_pos != current_positions[motor_id]:
                    current_positions[motor_id] = new_pos
                    ser.write(build_frame(key, motor_id, new_pos))
                    status_msgs.append(f"{name}:{new_pos}")

        # Display status
        if status_msgs:
            sys.stdout.write("\r\033[K-> " + " | ".join(status_msgs))
            sys.stdout.flush()

        # Refresh rate (0.01s = 100 Hz)
        time.sleep(0.01)

    print("\nDisconnecting from Eilik...")
    listener.stop()
    ser.close()

if __name__ == "__main__":
    main()
