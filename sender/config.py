from common.env import get_csv, get_float, get_int, get_str, load_env_file


load_env_file()

SERIAL_PORTS = get_csv("SENDER_SERIAL_PORTS", ["/dev/ttyUSB0", "/dev/ttyUSB1"])
BAUDRATE = get_int("SENDER_BAUDRATE", 115200)

RECEIVER_HOST = get_str("RECEIVER_HOST", "192.168.100.200")
RECEIVER_PORT = get_int("RECEIVER_PORT", 5000)

MOVEMENT_THRESHOLD = get_float("MOVEMENT_THRESHOLD", 0.35)
STOP_TIMEOUT = get_float("STOP_TIMEOUT", 0.5)

DISPLAY_INTERVAL = get_float("DISPLAY_INTERVAL", 0.2)
