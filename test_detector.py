import cv2
from recognition.detect import FaceDetector

MODEL_PATH = "models/detector/face_detection_yunet_2023mar.onnx"

camera = cv2.VideoCapture(0)

detector = FaceDetector(MODEL_PATH)

while True:
    ret, frame = camera.read()

    if not ret:
        break

    faces = detector.detect(frame)

    if faces is not None:
        for face in faces:
            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

    cv2.imshow("YuNet Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Tekan ESC untuk keluar
        break

camera.release()
cv2.destroyAllWindows()