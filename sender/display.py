import time

from sender import config
from sender.motion import current_summary


def display_loop(tracker):
    while True:
        with tracker.lock:
            _, summary_text = current_summary(tracker.state)
            right = tracker.state["R"]
            left = tracker.state["L"]

            text = (
                f"\r状態: {summary_text} | "
                f"R=({right['ax']:.3f},{right['ay']:.3f},{right['az']:.3f}) {'moving' if right['moving'] else 'stopped'} | "
                f"L=({left['ax']:.3f},{left['ay']:.3f},{left['az']:.3f}) {'moving' if left['moving'] else 'stopped'}   "
            )

        print(text, end="", flush=True)
        time.sleep(config.DISPLAY_INTERVAL)
