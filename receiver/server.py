import json
import socket

from receiver import config


def handle_client(conn, addr, event_processor):
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
                    event_processor.handle_event(data, line)
                except json.JSONDecodeError:
                    print(f"[WARN] JSON decode failed: {line}")

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        conn.close()
        print(f"[INFO] Disconnected: {addr}")


def serve(event_processor):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((config.HOST, config.PORT))
        server.listen()
        print(f"[INFO] Listening on {config.HOST}:{config.PORT}")

        while True:
            conn, addr = server.accept()
            handle_client(conn, addr, event_processor)
