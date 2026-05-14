import csv
import time


CSV_HEADER = [
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


def make_csv_file(events):
    ts = time.strftime("%Y%m%d_%H%M%S")
    ms = int((time.time() % 1) * 1000)
    filename = f"motion_batch_{ts}_{ms:03d}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

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
