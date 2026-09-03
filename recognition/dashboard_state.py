import time

dashboard_state = {
    "camera": False,
    "name": "-",
    "person_id": "-",
    "confidence": 0,
    "status": "Menunggu",
    "face_count": 0,
    "fps": 0,
    "last_update": time.time(),

    # Liveness challenge
    "liveness_state": "IDLE",
    "liveness_instruction": "Menunggu wajah dikenali",
    "liveness_direction": "UNKNOWN",
    "liveness_progress": 0,
    "liveness_required": 4,
    "liveness_remaining": 0,
    "liveness_message": "-"
}
