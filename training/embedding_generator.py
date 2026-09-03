import cv2

from recognition.detect import FaceDetector
from recognition.recognize import FaceRecognizer
from recognition.quality import FaceQuality

from config import (
    YUNET_MODEL_PATH,
    SFACE_MODEL_PATH,
    QUALITY_THRESHOLD
)


class EmbeddingGenerator:

    def __init__(self):

        self.detector = FaceDetector(
            str(YUNET_MODEL_PATH)
        )

        self.recognizer = FaceRecognizer(
            str(SFACE_MODEL_PATH)
        )

    def generate(self, image_path):
        """
        Membuat satu embedding wajah dari satu gambar dataset.

        Gambar hanya diterima jika:
        - dapat dibaca
        - tepat satu wajah terdeteksi
        - crop wajah valid
        - kualitas wajah memenuhi threshold
        """

        try:

            image = cv2.imread(image_path)

            if image is None:
                print(
                    "[IMAGE ERROR] {}".format(
                        image_path
                    )
                )
                return None

            faces = self.detector.detect(image)

            # ==========================
            # Tidak ada wajah
            # ==========================
            if faces is None or len(faces) == 0:

                print(
                    "[NO FACE] {}".format(
                        image_path
                    )
                )

                return None

            # ==========================
            # Lebih dari satu wajah
            # ==========================
            if len(faces) != 1:

                print(
                    "[MULTIPLE FACES] {} | jumlah={}".format(
                        image_path,
                        len(faces)
                    )
                )

                return None

            face = faces[0]

            # ==========================
            # Crop wajah
            # ==========================
            crop = self.detector.crop_face(
                image,
                face
            )

            if (
                crop is None
                or getattr(crop, "size", 0) == 0
            ):

                print(
                    "[INVALID CROP] {}".format(
                        image_path
                    )
                )

                return None

            # ==========================
            # Validasi kualitas
            # ==========================
            quality = FaceQuality.score(crop)

            if quality["score"] < QUALITY_THRESHOLD:

                print(
                    "[BAD QUALITY] {} | score={}".format(
                        image_path,
                        quality["score"]
                    )
                )

                return None

            # ==========================
            # Generate embedding
            # ==========================
            embedding = self.recognizer.extract(
                image,
                face
            )

            if embedding is None:

                print(
                    "[EMBEDDING ERROR] {}".format(
                        image_path
                    )
                )

                return None

            if getattr(embedding, "size", 0) == 0:

                print(
                    "[EMPTY EMBEDDING] {}".format(
                        image_path
                    )
                )

                return None

            print(
                "[OK EMBEDDING] {}".format(
                    image_path
                )
            )

            return embedding

        except cv2.error as error:

            print(
                "[OPENCV ERROR] {}: {}".format(
                    image_path,
                    error
                )
            )

            return None

        except Exception as error:

            print(
                "[GENERATOR ERROR] {}: {}".format(
                    image_path,
                    error
                )
            )

            return None
