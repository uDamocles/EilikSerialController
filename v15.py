import serial
import time
import threading
import tty
import sys
import termios

# --- CONFIGURATION ---
PORT_MAC = '/dev/tty.usbmodem21301'
BAUD_RATE = 125000
HB1 = bytes.fromhex("aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad")

# Built-in key mapping
COMMANDS = {
    # Left Arm (ID 2)
    'a': ("Left Arm High", 2, 2500),
    'z': ("Left Arm 66", 2, 2000),    
    'e': ("Left Arm Middle", 2, 1500),
    'r': ("Left Arm 33", 2, 1000),
    't': ("Left Arm Low", 2, 500),

    # Right Arm (ID 1)
    'y': ("Right Arm High", 1, 500),
    'u': ("Right Arm 66", 1, 1000),
    'i': ("Right Arm Middle", 1, 1500),
    'o': ("Right Arm 33", 1, 2000),
    'p': ("Right Arm Low", 1, 2500),

    # Head (ID 4)
    'q': ("Head Left", 4, 500),
    's': ("Head Mid-Left", 4, 1000),
    'd': ("Head Middle", 4, 1500),
    'f': ("Head Mid-Right", 4, 2000),
    'g': ("Head Right", 4, 2500),
    
    # Torso (ID 3)
    'w': ("Torso Left", 3, 2500),
    'x': ("Torso Mid-Left", 3, 2000),
    'c': ("Torso Middle", 3, 1500),
    'v': ("Torso Mid-Right", 3, 1000),
    'b': ("Torso Right", 3, 500),
    
    # Global command
    '0': ("FULL RESET (Middle)", None, 1500)
}

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def build_frame(token, motor_id, position):
    pos_bytes = position.to_bytes(2, byteorder='little')
    payload = bytes.fromhex("14 00 61") + token + bytes.fromhex("03 01") + bytes([motor_id]) + bytes.fromhex("01") + pos_bytes + bytes.fromhex("00 00 00 00 00")
    checksum = 255 - (sum(payload) % 256)
    return bytes.fromhex("aa aa aa") + payload + bytes([checksum])

def keep_alive(ser):
    while True:
        ser.write(HB1)
        time.sleep(2.0)

def display_menu():
    print("\n--- EILIK CONTROL MENU ---")
    for key, (name, _, _) in COMMANDS.items():
        print(f"[{key}] {name}")
    print("[!] Quit")
    print("--------------------------")

def main():
    ser = serial.Serial(PORT_MAC, BAUD_RATE, timeout=1)
    ser.rts = False; ser.dtr = True; time.sleep(1)
    
    ser.reset_input_buffer()
    ser.write(HB1)
    time.sleep(0.3)
    rep = ser.read(ser.in_waiting)
    key = rep[6:11] if len(rep) >= 11 else None
    
    if not key:
        print("Error: Unable to connect to Eilik."); return

    threading.Thread(target=keep_alive, args=(ser,), daemon=True).start()
    
    display_menu()
    while True:
        k = getch()
        if k == '!': break
        
        if k == '0':
            status = "-> Full reset in progress..."
            for motor in [1, 2, 3, 4]:
                ser.write(build_frame(key, motor, 1500))
                time.sleep(0.1)
        elif k in COMMANDS:
            name, mid, pos = COMMANDS[k]
            ser.write(build_frame(key, mid, pos))
            status = f"-> Action executing: {name} (Pos: {pos})"
        else:
            status = f"-> Unknown key '{k}'."
        
        # \r : carriage return, \033[K : clear line
        sys.stdout.write(f"\r\033[K{status}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
