import json
import socket
import threading
import time

import serial

# ===== 設定 =====
SERIAL_PORTS = [
    "/dev/ttyUSB0",
    "/dev/ttyUSB1",
]
BAUDRATE = 115200

# 受信側ラズパイのIPとポート
RECEIVER_HOST = "192.168.100.200"
RECEIVER_PORT = 5000

# 動き判定
MOVEMENT_THRESHOLD = 0.35
STOP_TIMEOUT = 0.5

# ターミナル表示更新間隔
DISPLAY_INTERVAL = 0.2

state = {
    "R": {
        "prev": None,
        "moving": False,
        "last_move_time": 0.0,
        "ax": 0.0,
        "ay": 0.0,
        "az": 0.0,
    },
    "L": {
        "prev": None,
        "moving": False,
        "last_move_time": 0.0,
        "ax": 0.0,
        "ay": 0.0,
        "az": 0.0,
    },
}

lock = threading.Lock()
last_sent_summary = None
client_socket = None


def connect_to_receiver():
    global client_socket

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RECEIVER_HOST, RECEIVER_PORT))
            client_socket = s
            print(f"[INFO] Connected to receiver {RECEIVER_HOST}:{RECEIVER_PORT}")
            return
        except Exception as e:
            print(f"[WARN] Receiver connection failed: {e}")
            time.sleep(2)


def send_json(data: dict):
    global client_socket

    line = json.dumps(data, ensure_ascii=False) + "\n"

    while True:
        try:
            if client_socket is None:
                connect_to_receiver()

            client_socket.sendall(line.encode("utf-8"))
            return
        except Exception as e:
            print(f"\n[WARN] Send failed: {e}")
            try:
                client_socket.close()
            except Exception:
                pass
            client_socket = None
            time.sleep(1)


def parse_line(line: str):
    parts = line.strip().split(",")
    if len(parts) != 4:
        return None

    hand = parts[0].strip()
    if hand not in ("R", "L"):
        return None

    try:
        ax = float(parts[1])
        ay = float(parts[2])
        az = float(parts[3])
    except ValueError:
        return None

    return hand, ax, ay, az


def calc_movement(prev, curr):
    dx = abs(curr[0] - prev[0])
    dy = abs(curr[1] - prev[1])
    dz = abs(curr[2] - prev[2])
    return dx + dy + dz


def current_summary():
    right_moving = state["R"]["moving"]
    left_moving = state["L"]["moving"]

    if right_moving and left_moving:
        return "both_moving", "両手が動いています"
    elif right_moving:
        return "right_moving", "右手が動いています"
    elif left_moving:
        return "left_moving", "左手が動いています"
    else:
        return "stopped", "どちらも止まっています"


def send_event(summary_key, summary_text):
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

    send_json(payload)
    print(f"\n[SEND] {summary_text}")


def update_hand_state(hand: str, ax: float, ay: float, az: float):
    global last_sent_summary

    now = time.time()
    curr = (ax, ay, az)

    with lock:
        s = state[hand]
        prev = s["prev"]

        s["ax"] = ax
        s["ay"] = ay
        s["az"] = az

        if prev is not None:
            movement = calc_movement(prev, curr)

            if movement > MOVEMENT_THRESHOLD:
                s["moving"] = True
                s["last_move_time"] = now
            else:
                if now - s["last_move_time"] > STOP_TIMEOUT:
                    s["moving"] = False
        else:
            s["last_move_time"] = now

        s["prev"] = curr

        summary_key, summary_text = current_summary()

        if summary_key != last_sent_summary:
            send_event(summary_key, summary_text)
            last_sent_summary = summary_key


def read_serial(port_name: str):
    try:
        ser = serial.Serial(port_name, BAUDRATE, timeout=1)
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
            update_hand_state(hand, ax, ay, az)

        except Exception as e:
            print(f"\n[ERROR] {port_name}: {e}")


def display_loop():
    while True:
        with lock:
            _, summary_text = current_summary()
            r = state["R"]
            l = state["L"]

            text = (
                f"\r状態: {summary_text} | "
                f"R=({r['ax']:.3f},{r['ay']:.3f},{r['az']:.3f}) {'moving' if r['moving'] else 'stopped'} | "
                f"L=({l['ax']:.3f},{l['ay']:.3f},{l['az']:.3f}) {'moving' if l['moving'] else 'stopped'}   "
            )

        print(text, end="", flush=True)
        time.sleep(DISPLAY_INTERVAL)


def main():
    connect_to_receiver()

    for port in SERIAL_PORTS:
        threading.Thread(target=read_serial, args=(port,), daemon=True).start()

    threading.Thread(target=display_loop, daemon=True).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
