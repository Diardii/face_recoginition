import cv2
import os
import time

from recognition.detect import FaceDetector
from recognition.quality import FaceQuality
from config import YUNET_MODEL_PATH, QUALITY_THRESHOLD

class SmartCapture:

    def __init__(self, dataset_path):

        self.detector = FaceDetector(
            str(YUNET_MODEL_PATH)
        )

        self.dataset_path = dataset_path

        self.last_capture = 0

        self.capture_interval = 1.2

        self.total_capture = 0

    def process(self, frame):

        faces = self.detector.detect(frame)

        if faces is None:

            return frame

        for face in faces:

            crop = self.detector.crop_face(
                frame,
                face
            )

            if crop.size == 0:
                continue

            quality = FaceQuality.score(crop)

            face = face.flatten()

            x = int(face[0])
            y = int(face[1])
            w = int(face[2])
            h = int(face[3])

            color = (0,0,255)

            if quality["score"] >= QUALITY_THRESHOLD:

                color = (0,255,0)

                now = time.time()

                if now-self.last_capture > self.capture_interval:

                    filename = os.path.join(
                        self.dataset_path,
                        f"{self.total_capture+1:03d}.jpg"
                    )

                    cv2.imwrite(
                        filename,
                        crop
                    )

                    self.total_capture += 1

                    self.last_capture = now

                    print(
                        f"Capture {self.total_capture}"
                    )

            cv2.rectangle(
                frame,
                (x,y),
                (x+w,y+h),
                color,
                2
            )

            cv2.putText(
                frame,
                f"{self.total_capture}/20",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

        return frame
