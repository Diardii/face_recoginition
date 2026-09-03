from recognition.camera import CameraManager
from recognition.detect import FaceDetector
from recognition.liveness.challenge_manager import ChallengeManager
from config import YUNET_MODEL_PATH


camera = CameraManager()

detector = FaceDetector(
    str(YUNET_MODEL_PATH)
)

challenge_manager = ChallengeManager()


if not camera.start():
    raise RuntimeError("Kamera gagal dibuka.")

person_id = "TEST001"

result = challenge_manager.start(person_id)

print("===================================")
print(result["instruction"])
print("===================================")

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

        if len(faces) > 1:
            print("MULTIPLE FACES")
            continue

        result = challenge_manager.process(
            faces[0],
            person_id
        )

        print(
            "Target: {:<5} | Arah: {:<7} | "
            "Frame: {}/{} | Sisa: {} | {}".format(
                result["challenge"],
                result["direction"],
                result["match_count"],
                result["confirm_frames"],
                result["remaining"],
                result["state"]
            )
        )

        if result["passed"]:
            print("LIVENESS BERHASIL")
            break

        if result["failed"]:
            print("LIVENESS GAGAL")
            break

except KeyboardInterrupt:
    print("\nTes dihentikan.")

finally:
    camera.stop()
