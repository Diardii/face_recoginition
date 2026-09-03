import cv2
import os
import time
from datetime import datetime

from database.database import (
    save_attendance,
    attendance_exists
)
from config import (
    ATTENDANCE_COOLDOWN,
    ATTENDANCE_IMAGES_DIR
)


class AttendanceManager:

    def __init__(self, cooldown=ATTENDANCE_COOLDOWN):
        """
        cooldown = jeda minimal dalam detik sebelum pemeriksaan
        ulang untuk orang dan jenis absensi yang sama.
        """
        self.cooldown = cooldown
        self.last_detection = {}

    def can_save(self, person_id, attendance_type):

        key = (
            person_id,
            attendance_type
        )

        now = time.time()
        last_time = self.last_detection.get(key)

        if last_time is None:
            return True

        return (now - last_time) >= self.cooldown

    def mark_checked(self, person_id, attendance_type):
        """
        Mencatat waktu pemeriksaan terakhir berdasarkan
        person dan jenis absensi.
        """

        key = (
            person_id,
            attendance_type
        )

        self.last_detection[key] = time.time()

    def save(
        self,
        person,
        frame=None,
        attendance_type=None
    ):

        person_id = person.get("person_id")
        person_name = person.get("name")
        confidence = person.get("score", 0)

        if attendance_type not in (
            "Masuk",
            "Pulang"
        ):
            print(
                "[ATTENDANCE] Jenis absensi tidak valid:",
                attendance_type
            )
            return False

        if not person_id or not person_name:
            print("[ATTENDANCE] Data person tidak lengkap.")
            return False

        if not self.can_save(
            person_id,
            attendance_type
        ):
            return False

        self.mark_checked(
            person_id,
            attendance_type
        )

        if attendance_exists(
            person_id=person_id,
            attendance_type=attendance_type
        ):
            print(
                "[ATTENDANCE] {} ({}) sudah absen {} hari ini.".format(
                    person_name,
                    person_id,
                    attendance_type
                )
            )
            return False

        image_path = None

        if frame is not None:

            os.makedirs(
                str(ATTENDANCE_IMAGES_DIR),
                exist_ok=True
            )

            filename = (
                datetime.now().strftime("%Y%m%d_%H%M%S")
                + "_"
                + person_id
                + "_"
                + attendance_type.lower()
                + ".jpg"
            )

            image_path = str(
                ATTENDANCE_IMAGES_DIR / filename
            )

            image_saved = cv2.imwrite(
                image_path,
                frame
            )

            if not image_saved:
                print("[ATTENDANCE] Foto gagal disimpan.")
                image_path = None

        saved = save_attendance(
            person_id=person_id,
            person_name=person_name,
            attendance_type=attendance_type,
            confidence=confidence,
            image=image_path
        )

        if not saved:

            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except OSError as error:
                    print(
                        "[ATTENDANCE] Gagal menghapus foto:",
                        error
                    )

            print(
                "[ATTENDANCE] {} ({}) tidak disimpan.".format(
                    person_name,
                    person_id
                )
            )
            return False

        print(
            "[ATTENDANCE] {} ({}) berhasil disimpan sebagai {}.".format(
                person_name,
                person_id,
                attendance_type
            )
        )

        return True
