import numpy as np

from config import HEAD_TURN_THRESHOLD


class HeadPoseEstimator:
    """
    Estimasi arah kepala kasar dari 5 landmark YuNet.

    Output:
        FRONT
        LEFT
        RIGHT
        UNKNOWN

    Catatan:
        Ini bukan estimasi pose 3D penuh. Modul ini menggunakan
        pergeseran posisi hidung terhadap titik tengah kedua mata.
    """

    FRONT = "FRONT"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UNKNOWN = "UNKNOWN"

    def __init__(self, threshold=HEAD_TURN_THRESHOLD):
        self.threshold = float(threshold)

    def estimate(self, face):
        if face is None:
            return self._unknown_result("Data wajah kosong.")

        values = np.asarray(face).flatten()

        # YuNet menghasilkan:
        # x, y, w, h,
        # landmark mata 1,
        # landmark mata 2,
        # hidung,
        # sudut mulut 1,
        # sudut mulut 2,
        # score
        if values.size < 14:
            return self._unknown_result(
                "Landmark YuNet tidak lengkap."
            )

        eye_1_x = float(values[4])
        eye_1_y = float(values[5])

        eye_2_x = float(values[6])
        eye_2_y = float(values[7])

        nose_x = float(values[8])
        nose_y = float(values[9])

        eye_center_x = (eye_1_x + eye_2_x) / 2.0
        eye_center_y = (eye_1_y + eye_2_y) / 2.0

        eye_distance = abs(eye_2_x - eye_1_x)

        if eye_distance < 1.0:
            return self._unknown_result(
                "Jarak landmark mata tidak valid."
            )

        # Normalisasi agar tetap relatif stabil terhadap jarak kamera.
        horizontal_offset = (
            nose_x - eye_center_x
        ) / eye_distance

        if horizontal_offset <= -self.threshold:
            direction = self.RIGHT

        elif horizontal_offset >= self.threshold:
            direction = self.LEFT

        else:
            direction = self.FRONT

        print(
            "[HEAD POSE]",
            "offset=", round(horizontal_offset, 4),
            "direction=", direction,
            "threshold=", self.threshold
        )

        return {
            "valid": True,
            "direction": direction,
            "offset": round(horizontal_offset, 4),
            "threshold": self.threshold,
            "eye_center": (
                round(eye_center_x, 2),
                round(eye_center_y, 2)
            ),
            "nose": (
                round(nose_x, 2),
                round(nose_y, 2)
            ),
            "message": "Pose wajah berhasil diperkirakan."
        }

    def _unknown_result(self, message):
        return {
            "valid": False,
            "direction": self.UNKNOWN,
            "offset": 0.0,
            "threshold": self.threshold,
            "eye_center": None,
            "nose": None,
            "message": message
        }
