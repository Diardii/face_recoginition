import cv2

from recognition.detect import FaceDetector
from recognition.quality import FaceQuality

MODEL_PATH = "models/detector/face_detection_yunet_2023mar.onnx"

detector = FaceDetector(MODEL_PATH)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera tidak dapat dibuka")
    exit()

while True:

    ret, frame = camera.read()

    if not ret:
        break

    faces = detector.detect(frame)

    if faces is not None:

        for face in faces:

            # Crop wajah
            crop = detector.crop_face(frame, face)

            if crop.size == 0:
                continue

            # Hitung kualitas
            quality = FaceQuality.score(crop)

            # Koordinat wajah
            face = face.flatten()

            x = int(face[0])
            y = int(face[1])
            w = int(face[2])
            h = int(face[3])

            # Warna kotak
            if quality["score"] >= 80:
                color = (0, 255, 0)
                status = "GOOD"
            else:
                color = (0, 0, 255)
                status = "BAD"

            # Kotak wajah
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                2
            )

            # Informasi
            cv2.putText(
                frame,
                f"{status}  Q:{quality['score']}%",
                (x, y - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            cv2.putText(
                frame,
                f"B:{quality['brightness']:.0f}",
                (x, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            cv2.putText(
                frame,
                f"BL:{quality['blur']:.0f}",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

    cv2.imshow("Smart Face Quality Test", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

camera.release()
cv2.destroyAllWindows()