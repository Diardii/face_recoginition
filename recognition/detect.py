import cv2


class FaceDetector:

    def __init__(self, model_path):

        self.detector = cv2.FaceDetectorYN.create(
            model=model_path,
            config="",
            input_size=(320, 320),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=5000
        )

    def detect(self, frame):

        h, w = frame.shape[:2]

        self.detector.setInputSize((w, h))

        _, faces = self.detector.detect(frame)

        return faces

    def crop_face(self, frame, face):

        face = face.flatten()

        x = int(face[0])
        y = int(face[1])
        w = int(face[2])
        h = int(face[3])

        x = max(0, x)
        y = max(0, y)

        return frame[y:y+h, x:x+w]