from recognition.detect import FaceDetector
from recognition.quality import FaceQuality

from config import (
    YUNET_MODEL_PATH,
    QUALITY_THRESHOLD
)


class DatasetValidator:

    def __init__(self):

        self.detector = FaceDetector(
            str(YUNET_MODEL_PATH)
        )

    def validate(self, image):
        """
        Memeriksa apakah gambar layak dimasukkan ke dataset.

        Return dictionary:
            valid   : True atau False
            message : pesan hasil validasi
            crop    : hasil crop wajah jika valid
            quality : detail kualitas wajah
            face    : data deteksi YuNet
        """

        if image is None:
            return {
                "valid": False,
                "message": "Gambar tidak dapat dibaca.",
                "crop": None,
                "quality": None,
                "face": None
            }

        if getattr(image, "size", 0) == 0:
            return {
                "valid": False,
                "message": "Gambar kosong.",
                "crop": None,
                "quality": None,
                "face": None
            }

        try:
            faces = self.detector.detect(image)

        except Exception as error:
            return {
                "valid": False,
                "message": "Deteksi wajah gagal: {}".format(error),
                "crop": None,
                "quality": None,
                "face": None
            }

        if faces is None or len(faces) == 0:
            return {
                "valid": False,
                "message": "Wajah tidak ditemukan.",
                "crop": None,
                "quality": None,
                "face": None
            }

        if len(faces) > 1:
            return {
                "valid": False,
                "message": (
                    "Terdeteksi lebih dari satu wajah. "
                    "Pastikan hanya satu orang di depan kamera."
                ),
                "crop": None,
                "quality": None,
                "face": None
            }

        face = faces[0]

        crop = self.detector.crop_face(
            image,
            face
        )

        if crop is None or getattr(crop, "size", 0) == 0:
            return {
                "valid": False,
                "message": "Area wajah gagal dipotong.",
                "crop": None,
                "quality": None,
                "face": face
            }

        try:
            quality = FaceQuality.score(crop)

        except Exception as error:
            return {
                "valid": False,
                "message": "Pemeriksaan kualitas gagal: {}".format(error),
                "crop": None,
                "quality": None,
                "face": face
            }

        if not quality["brightness_ok"]:
            return {
                "valid": False,
                "message": (
                    "Wajah terlalu gelap. "
                    "Tambahkan pencahayaan."
                ),
                "crop": crop,
                "quality": quality,
                "face": face
            }

        if not quality["blur_ok"]:
            return {
                "valid": False,
                "message": (
                    "Wajah terlalu buram. "
                    "Diamkan kepala dan bersihkan kamera."
                ),
                "crop": crop,
                "quality": quality,
                "face": face
            }

        if not quality["size_ok"]:
            return {
                "valid": False,
                "message": (
                    "Wajah terlalu kecil. "
                    "Dekatkan wajah ke kamera."
                ),
                "crop": crop,
                "quality": quality,
                "face": face
            }

        if quality["score"] < QUALITY_THRESHOLD:
            return {
                "valid": False,
                "message": "Kualitas wajah belum memenuhi syarat.",
                "crop": crop,
                "quality": quality,
                "face": face
            }

        return {
            "valid": True,
            "message": "Gambar wajah valid.",
            "crop": crop,
            "quality": quality,
            "face": face
        }
