import csv
import json
import socket
import time
from ftplib import FTP
from pathlib import Path

HOST = "0.0.0.0"
PORT = 5000
LOG_FILE = "motion_log.jsonl"

# ===== FTP送信先を2台定義 =====
FTP_TARGETS = [
    {
        "host": "192.168.100.7",  # 1台目PCのIP
        "user": "user1",
        "password": "password1",
        "upload_dir": "",
    },
    {
        "host": "192.168.100.8",  # 2台目PCのIP
        "user": "user2",
        "password": "password2",
        "upload_dir": "",
    },
]

# ===== 何件ごとにCSV送信するか =====
BATCH_SIZE = 10

buffered_events = []


def save_log(line: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def print_event(data: dict):
    timestamp = data.get("timestamp", time.time())
    t = time.strftime("%H:%M:%S", time.localtime(timestamp))

    summary_text = data.get("summary_text", "不明")
    right = data.get("right", {})
    left = data.get("left", {})

    print("\n" + "=" * 50)
    print(f"[{t}] {summary_text}")
    print(
        f"右手: {'moving' if right.get('moving') else 'stopped'} "
        f"(ax={right.get('ax', 0):.3f}, ay={right.get('ay', 0):.3f}, az={right.get('az', 0):.3f})"
    )
    print(
        f"左手: {'moving' if left.get('moving') else 'stopped'} "
        f"(ax={left.get('ax', 0):.3f}, ay={left.get('ay', 0):.3f}, az={left.get('az', 0):.3f})"
    )
    print("=" * 50)


def make_csv_file(events):
    ts = time.strftime("%Y%m%d_%H%M%S")
    ms = int((time.time() % 1) * 1000)
    filename = f"motion_batch_{ts}_{ms:03d}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "timestamp",
                "time_text",
                "summary_key",
                "summary_text",
                "right_moving",
                "right_ax",
                "right_ay",
                "right_az",
                "left_moving",
                "left_ax",
                "left_ay",
                "left_az",
            ]
        )

        for event in events:
            timestamp = event.get("timestamp", time.time())
            time_text = time.strftime("%H:%M:%S", time.localtime(timestamp))
            right = event.get("right", {})
            left = event.get("left", {})

            writer.writerow(
                [
                    timestamp,
                    time_text,
                    event.get("summary_key", ""),
                    event.get("summary_text", ""),
                    int(bool(right.get("moving", False))),
                    right.get("ax", 0),
                    right.get("ay", 0),
                    right.get("az", 0),
                    int(bool(left.get("moving", False))),
                    left.get("ax", 0),
                    left.get("ay", 0),
                    left.get("az", 0),
                ]
            )

    return filename


def upload_file_to_one_target(filepath, target):
    with FTP(target["host"]) as ftp:
        ftp.login(target["user"], target["password"])

        if target.get("upload_dir"):
            ftp.cwd(target["upload_dir"])

        with open(filepath, "rb") as f:
            ftp.storbinary(f"STOR {Path(filepath).name}", f)

    print(f"[FTP] Uploaded to {target['host']}: {filepath}")


def upload_file_to_all_targets(filepath):
    failed_targets = []

    for target in FTP_TARGETS:
        try:
            upload_file_to_one_target(filepath, target)
        except Exception as e:
            print(f"[FTP ERROR] {target['host']} -> {e}")
            failed_targets.append(target["host"])

    return failed_targets


def process_batch_if_needed():
    global buffered_events

    if len(buffered_events) >= BATCH_SIZE:
        batch = buffered_events[:BATCH_SIZE]
        buffered_events = buffered_events[BATCH_SIZE:]

        try:
            csv_file = make_csv_file(batch)
            failed_targets = upload_file_to_all_targets(csv_file)

            if failed_targets:
                print(f"[WARN] Failed targets: {failed_targets}")
                buffered_events = batch + buffered_events
            else:
                # 送信成功後にCSVを消したいなら次の行を有効化
                # Path(csv_file).unlink(missing_ok=True)
                pass

        except Exception as e:
            print(f"[BATCH ERROR] {e}")
            buffered_events = batch + buffered_events


def handle_event(data: dict, raw_line: str):
    global buffered_events

    save_log(raw_line)
    print_event(data)

    buffered_events.append(data)
    process_batch_if_needed()


def handle_client(conn, addr):
    print(f"[INFO] Connected from {addr}")
    buffer = ""

    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break

            buffer += chunk.decode("utf-8", errors="ignore")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)
                    handle_event(data, line)
                except json.JSONDecodeError:
                    print(f"[WARN] JSON decode failed: {line}")

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[INFO] Disconnected: {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[INFO] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)


if __name__ == "__main__":
    main()
