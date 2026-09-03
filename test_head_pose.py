import cv2

from recognition.camera import CameraManager
from recognition.detect import FaceDetector
from recognition.liveness.head_pose import HeadPoseEstimator
from config import YUNET_MODEL_PATH


camera = CameraManager()

detector = FaceDetector(
    str(YUNET_MODEL_PATH)
)

pose_estimator = HeadPoseEstimator()


if not camera.start():
    raise RuntimeError("Kamera gagal dibuka.")

print("Tes arah kepala dimulai.")
print("Hadap depan, lalu menoleh kiri dan kanan.")
print("Tekan Ctrl+C untuk berhenti.")

try:
    while camera.is_running():

        success, frame = camera.read()

        if not success or frame is None:
            print("Frame kamera gagal dibaca.")
            break

        faces = detector.detect(frame)

        if faces is None or len(faces) == 0:
            print("NO FACE")
            continue

        # Kalibrasi hanya memakai satu wajah.
        if len(faces) > 1:
            print("MULTIPLE FACES")
            continue

        result = pose_estimator.estimate(faces[0])

        print(
            "Direction: {:<7} Offset: {}".format(
                result["direction"],
                result["offset"]
            )
        )

except KeyboardInterrupt:
    print("\nTes dihentikan.")

finally:
    camera.stop()
