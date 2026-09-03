import cv2
import numpy as np


class FaceQuality:

    BRIGHTNESS_THRESHOLD = 50
    BLUR_THRESHOLD = 30
    MIN_FACE_SIZE = 120

    @staticmethod
    def brightness(face):
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    @staticmethod
    def blur(face):
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    @staticmethod
    def size(face):
        h, w = face.shape[:2]
        return min(h, w)

    @staticmethod
    def score(face):

        brightness = FaceQuality.brightness(face)
        blur = FaceQuality.blur(face)
        size = FaceQuality.size(face)

        brightness_ok = brightness >= FaceQuality.BRIGHTNESS_THRESHOLD
        blur_ok = blur >= FaceQuality.BLUR_THRESHOLD
        size_ok = size >= FaceQuality.MIN_FACE_SIZE

        score = 0

        if brightness_ok:
            score += 35

        if blur_ok:
            score += 35

        if size_ok:
            score += 30

        return {
            "brightness": brightness,
            "blur": blur,
            "size": size,
            "score": score,
            "brightness_ok": brightness_ok,
            "blur_ok": blur_ok,
            "size_ok": size_ok
        }