from pathlib import Path


# ==================================================
# Direktori project
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models"
ATTENDANCE_IMAGES_DIR = BASE_DIR / "attendance_images"

DATABASE_PATH = BASE_DIR / "database" / "database.db"

EMBEDDINGS_PATH = (
    MODELS_DIR / "embeddings" / "embeddings.pkl"
)

TEMP_EMBEDDINGS_PATH = (
    MODELS_DIR / "embeddings" / "embeddings.tmp"
)


# ==================================================
# Model face recognition
# ==================================================

YUNET_MODEL_PATH = (
    MODELS_DIR
    / "detector"
    / "face_detection_yunet_2023mar.onnx"
)

SFACE_MODEL_PATH = (
    MODELS_DIR
    / "recognizer"
    / "face_recognition_sface_2021dec.onnx"
)


# ==================================================
# Kamera
# ==================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600
CAMERA_FPS = 30
CAMERA_SCAN_LIMIT = 10


# ==================================================
# Recognition
# ==================================================

QUALITY_THRESHOLD = 80
RECOGNITION_THRESHOLD = 0.60
RECOGNITION_INTERVAL = 3
DETECT_INTERVAL =3

# ==================================================
# Attendance
# ==================================================

ATTENDANCE_COOLDOWN = 5
DEFAULT_ATTENDANCE_TYPE = "Masuk"


# ==================================================
# Dataset dan training
# ==================================================

MAX_DATASET_PHOTOS = 20


# ==================================================
# Flask
# ==================================================

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False
FLASK_THREADED = True

# ==================================================
# Liveness challenge
# ==================================================

HEAD_TURN_THRESHOLD = 0.18
LIVENESS_CHALLENGE_TIMEOUT = 8
LIVENESS_CONFIRM_FRAMES = 3
