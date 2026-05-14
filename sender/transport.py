import json
import socket
import time

from sender import config


class ReceiverClient:
    def __init__(self):
        self.client_socket = None

    def connect_to_receiver(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((config.RECEIVER_HOST, config.RECEIVER_PORT))
                self.client_socket = sock
                print(f"[INFO] Connected to receiver {config.RECEIVER_HOST}:{config.RECEIVER_PORT}")
                return
            except Exception as e:
                print(f"[WARN] Receiver connection failed: {e}")
                time.sleep(2)

    def send_json(self, data: dict):
        line = json.dumps(data, ensure_ascii=False) + "\n"

        while True:
            try:
                if self.client_socket is None:
                    self.connect_to_receiver()

                self.client_socket.sendall(line.encode("utf-8"))
                return
            except Exception as e:
                print(f"\n[WARN] Send failed: {e}")
                self._close_socket()
                time.sleep(1)

    def _close_socket(self):
        try:
            if self.client_socket is not None:
                self.client_socket.close()
        except Exception:
            pass
        self.client_socket = None
