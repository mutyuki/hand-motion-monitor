from ftplib import FTP
from pathlib import Path

from receiver import config


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

    for target in config.FTP_TARGETS:
        try:
            upload_file_to_one_target(filepath, target)
        except Exception as e:
            print(f"[FTP ERROR] {target['host']} -> {e}")
            failed_targets.append(target["host"])

    return failed_targets
