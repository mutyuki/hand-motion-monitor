from common.env import get_int, get_json, get_str, load_env_file


DEFAULT_FTP_TARGETS = [
    {
        "host": "192.168.100.7",
        "user": "user1",
        "password": "password1",
        "upload_dir": "",
    },
    {
        "host": "192.168.100.8",
        "user": "user2",
        "password": "password2",
        "upload_dir": "",
    },
]


load_env_file()

HOST = get_str("RECEIVER_BIND_HOST", "0.0.0.0")
PORT = get_int("RECEIVER_BIND_PORT", 5000)
LOG_FILE = get_str("LOG_FILE", "motion_log.jsonl")
BATCH_SIZE = get_int("BATCH_SIZE", 10)
FTP_TARGETS = get_json("FTP_TARGETS_JSON", DEFAULT_FTP_TARGETS)
