import threading
import time

import serial

from sender import config
from sender.display import display_loop
from sender.motion import MotionTracker, parse_line
from sender.transport import ReceiverClient


def send_event(client, summary_key, summary_text, state):
    payload = {
        "timestamp": time.time(),
        "summary_key": summary_key,
        "summary_text": summary_text,
        "right": {
            "moving": state["R"]["moving"],
            "ax": state["R"]["ax"],
            "ay": state["R"]["ay"],
            "az": state["R"]["az"],
        },
        "left": {
            "moving": state["L"]["moving"],
            "ax": state["L"]["ax"],
            "ay": state["L"]["ay"],
            "az": state["L"]["az"],
        },
    }

    client.send_json(payload)
    print(f"\n[SEND] {summary_text}")


def read_serial(port_name: str, tracker: MotionTracker):
    try:
        ser = serial.Serial(port_name, config.BAUDRATE, timeout=1)
        print(f"[INFO] Opened {port_name}")
    except Exception as e:
        print(f"[ERROR] Could not open {port_name}: {e}")
        return

    while True:
        try:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                continue

            parsed = parse_line(raw)
            if parsed is None:
                print(f"\n[SKIP] {port_name}: {raw}")
                continue

            hand, ax, ay, az = parsed
            tracker.update_hand_state(hand, ax, ay, az)

        except Exception as e:
            print(f"\n[ERROR] {port_name}: {e}")


def main():
    client = ReceiverClient()
    tracker = MotionTracker(lambda key, text, state: send_event(client, key, text, state))

    client.connect_to_receiver()

    for port in config.SERIAL_PORTS:
        threading.Thread(target=read_serial, args=(port, tracker), daemon=True).start()

    threading.Thread(target=display_loop, args=(tracker,), daemon=True).start()

    while True:
        time.sleep(1)
