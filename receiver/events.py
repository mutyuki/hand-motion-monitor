import time

from receiver import config
from receiver.csv_export import make_csv_file
from receiver.ftp_upload import upload_file_to_all_targets


class EventProcessor:
    def __init__(self):
        self.buffered_events = []

    def handle_event(self, data: dict, raw_line: str):
        self.save_log(raw_line)
        print_event(data)

        self.buffered_events.append(data)
        self.process_batch_if_needed()

    def save_log(self, line: str):
        with open(config.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def process_batch_if_needed(self):
        if len(self.buffered_events) >= config.BATCH_SIZE:
            batch = self.buffered_events[: config.BATCH_SIZE]
            self.buffered_events = self.buffered_events[config.BATCH_SIZE :]

            try:
                csv_file = make_csv_file(batch)
                failed_targets = upload_file_to_all_targets(csv_file)

                if failed_targets:
                    print(f"[WARN] Failed targets: {failed_targets}")
                    self.buffered_events = batch + self.buffered_events
                else:
                    # 送信成功後にCSVを消したいなら次の行を有効化
                    # Path(csv_file).unlink(missing_ok=True)
                    pass

            except Exception as e:
                print(f"[BATCH ERROR] {e}")
                self.buffered_events = batch + self.buffered_events


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
