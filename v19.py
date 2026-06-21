import serial
import time
import threading
import sys
import os

# Configuration to force Pygame into "headless" mode
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

# --- SERIAL CONFIGURATION ---
PORT_MAC = '/dev/tty.usbmodem21301'
BAUD_RATE = 125000
HB1 = bytes.fromhex("aa aa aa 0a 00 61 e4 c6 f1 ca 83 ff ad")

# --- MOTOR CONFIGURATION ---
MIN_POS = 0
MAX_POS = 3000
STEP = 25  # Max movement speed per loop

# Current state of the motors
current_positions = {
    1: 1500, # Right Arm
    2: 1500, # Left Arm
    3: 1500, # Torso
    4: 1500  # Head
}

# --- CONTROLLER CONFIGURATION (Standard SDL2 Mapping) ---
# If an axis does not react correctly on your Mac, you can modify these values
AXIS_LS_X = 0      # Left Stick X (Torso)
AXIS_RS_X = 2      # Right Stick X (Head)
AXIS_LT   = 4      # Left Trigger (LT)
AXIS_RT   = 5      # Right Trigger (RT)
BTN_LB    = 9      # Left Bumper (LB)
BTN_RB    = 10     # Right Bumper (RB)
BTN_START = 6      # Start Button (Reset)

DEADZONE = 0.15    # Deadzone to prevent stick drift

running = True

def build_frame(token, motor_id, position):
    pos_bytes = int(position).to_bytes(2, byteorder='little')
    payload = bytes.fromhex("14 00 61") + token + bytes.fromhex("03 01") + bytes([motor_id]) + bytes.fromhex("01") + pos_bytes + bytes.fromhex("00 00 00 00 00")
    checksum = 255 - (sum(payload) % 256)
    return bytes.fromhex("aa aa aa") + payload + bytes([checksum])

def keep_alive(ser):
    while running:
        ser.write(HB1)
        time.sleep(2.0)

def display_menu(joystick_name):
    print("\n--- EILIK XBOX CONTROLLER (v19) ---")
    print(f"🎮 Controller connected: {joystick_name}")
    print("-----------------------------------")
    print("[Left Stick] Left/Right -> Torso")
    print("[Right Stick] Left/Right -> Head")
    print("[LB] / [LT] -> Left Arm (Up/Down)")
    print("[RB] / [RT] -> Right Arm (Up/Down)")
    print("[START] -> RESET to center position")
    print("[CTRL+C] in terminal to Quit")
    print("-----------------------------------")

def main():
    global running

    # Initialize Pygame and Joystick
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("Error: No Xbox or compatible controller detected.")
        sys.exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    try:
        ser = serial.Serial(PORT_MAC, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return

    ser.rts = False; ser.dtr = True; time.sleep(1)

    ser.reset_input_buffer()
    ser.write(HB1)
    time.sleep(0.3)
    rep = ser.read(ser.in_waiting)
    key = rep[6:11] if len(rep) >= 11 else None

    if not key:
        print("Error: Unable to obtain Eilik session key.")
        ser.close()
        return

    # Start Heartbeat
    threading.Thread(target=keep_alive, args=(ser,), daemon=True).start()

    display_menu(joystick.get_name())

    try:
        # Game Loop at ~100 Hz
        while running:
            pygame.event.pump() # Update controller state
            status_msgs = []
            deltas = {1: 0, 2: 0, 3: 0, 4: 0}

            # --- 1. RESET (Start) ---
            if joystick.get_button(BTN_START):
                for motor_id in current_positions.keys():
                    current_positions[motor_id] = 1500
                    ser.write(build_frame(key, motor_id, 1500))
                    time.sleep(0.01)
                sys.stdout.write("\r\033[K-> Full reset completed.")
                sys.stdout.flush()
                time.sleep(0.5) # Pause to prevent spamming the Reset
                continue

            # --- 2. TORSO AND HEAD (Analog Sticks) ---
            val_torso = joystick.get_axis(AXIS_LS_X)
            val_head = joystick.get_axis(AXIS_RS_X)

            if abs(val_torso) > DEADZONE:
                deltas[3] = -val_torso * STEP 
            if abs(val_head) > DEADZONE:
                deltas[4] = -val_head * STEP   

            # --- 3. LEFT AND RIGHT ARMS (Triggers and Bumpers) ---
            lb = joystick.get_button(BTN_LB)
            rb = joystick.get_button(BTN_RB)

            # Pygame returns -1.0 released and 1.0 pressed for triggers. Normalize 0.0 to 1.0
            lt_raw = joystick.get_axis(AXIS_LT) if joystick.get_numaxes() > AXIS_LT else -1.0
            rt_raw = joystick.get_axis(AXIS_RT) if joystick.get_numaxes() > AXIS_RT else -1.0
            lt = (lt_raw + 1.0) / 2.0
            rt = (rt_raw + 1.0) / 2.0

            # Left Arm (ID 2): LB=Up(+), LT=Down(-)
            if lb: deltas[2] += STEP
            if lt > DEADZONE: deltas[2] -= lt * STEP

            # Right Arm (ID 1): RB=Up(-), RT=Down(+)
            if rb: deltas[1] -= STEP
            if rt > DEADZONE: deltas[1] += rt * STEP

            # --- 4. APPLY TO MOTORS ---
            for motor_id, delta in deltas.items():
                if delta != 0:
                    new_pos = current_positions[motor_id] + delta
                    new_pos = max(MIN_POS, min(MAX_POS, new_pos))

                    if int(new_pos) != int(current_positions[motor_id]):
                        current_positions[motor_id] = new_pos
                        ser.write(build_frame(key, motor_id, int(new_pos)))

                        # Formatted display (e.g., Torso:1650)
                        names = {1: "RightArm", 2: "LeftArm", 3: "Torso", 4: "Head"}
                        status_msgs.append(f"{names[motor_id]}:{int(new_pos)}")

            # --- 5. CONSOLE DISPLAY ---
            if status_msgs:
                sys.stdout.write("\r\033[K-> " + " | ".join(status_msgs))
                sys.stdout.flush()

            time.sleep(0.01)

    except KeyboardInterrupt:
        # Exit cleanly with CTRL+C
        pass

    print("\nDisconnecting from Eilik...")
    running = False
    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
