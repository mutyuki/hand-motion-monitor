import threading
import time

from sender import config


def initial_state():
    return {
        "R": _initial_hand_state(),
        "L": _initial_hand_state(),
    }


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


def current_summary(state):
    right_moving = state["R"]["moving"]
    left_moving = state["L"]["moving"]

    if right_moving and left_moving:
        return "both_moving", "両手が動いています"
    if right_moving:
        return "right_moving", "右手が動いています"
    if left_moving:
        return "left_moving", "左手が動いています"
    return "stopped", "どちらも止まっています"


class MotionTracker:
    def __init__(self, send_event):
        self.state = initial_state()
        self.lock = threading.Lock()
        self.last_sent_summary = None
        self._send_event = send_event

    def update_hand_state(self, hand: str, ax: float, ay: float, az: float):
        now = time.time()
        curr = (ax, ay, az)

        with self.lock:
            hand_state = self.state[hand]
            prev = hand_state["prev"]

            hand_state["ax"] = ax
            hand_state["ay"] = ay
            hand_state["az"] = az

            if prev is not None:
                movement = calc_movement(prev, curr)

                if movement > config.MOVEMENT_THRESHOLD:
                    hand_state["moving"] = True
                    hand_state["last_move_time"] = now
                elif now - hand_state["last_move_time"] > config.STOP_TIMEOUT:
                    hand_state["moving"] = False
            else:
                hand_state["last_move_time"] = now

            hand_state["prev"] = curr

            summary_key, summary_text = current_summary(self.state)

            if summary_key != self.last_sent_summary:
                self._send_event(summary_key, summary_text, self.state)
                self.last_sent_summary = summary_key


def _initial_hand_state():
    return {
        "prev": None,
        "moving": False,
        "last_move_time": 0.0,
        "ax": 0.0,
        "ay": 0.0,
        "az": 0.0,
    }
