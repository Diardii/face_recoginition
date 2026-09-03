import threading


VALID_ATTENDANCE_TYPES = (
    "Masuk",
    "Pulang"
)

_state_lock = threading.Lock()

_attendance_state = {
    "type": None
}


def set_attendance_mode(attendance_type):

    if attendance_type not in VALID_ATTENDANCE_TYPES:
        return False

    with _state_lock:
        _attendance_state["type"] = attendance_type

    return True


def get_attendance_mode():

    with _state_lock:
        return _attendance_state["type"]


def clear_attendance_mode():

    with _state_lock:
        _attendance_state["type"] = None
