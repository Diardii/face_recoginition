import cv2
import time
import threading

from recognition.camera import CameraManager
from recognition.detect import FaceDetector
from recognition.quality import FaceQuality
from recognition.recognize import FaceRecognizer
from recognition.attendance_manager import AttendanceManager
from recognition.dashboard_state import dashboard_state
from recognition.liveness.challenge_manager import ChallengeManager
from database.database import attendance_exists
from recognition.attendance_state import get_attendance_mode
from config import (
    YUNET_MODEL_PATH,
    SFACE_MODEL_PATH,
    QUALITY_THRESHOLD,
    ATTENDANCE_COOLDOWN,
    RECOGNITION_INTERVAL
)


camera_manager = CameraManager()

detector = FaceDetector(
    str(YUNET_MODEL_PATH)
)

recognizer = FaceRecognizer(
    str(SFACE_MODEL_PATH)
)

attendance_manager = AttendanceManager(
    cooldown=ATTENDANCE_COOLDOWN
)

# Digunakan hanya sebagai referensi konfigurasi dashboard.
challenge_manager = ChallengeManager()

# Hanya satu generator yang boleh memproses recognition/liveness.
# Ini mencegah dua tab atau dua koneksi video menyimpan absensi
# secara bersamaan.
recognition_stream_lock = threading.Lock()


def reset_liveness_dashboard(
    instruction="Menunggu wajah dikenali",
    message="-"
):
    dashboard_state["liveness_state"] = "IDLE"
    dashboard_state["liveness_instruction"] = instruction
    dashboard_state["liveness_direction"] = "UNKNOWN"
    dashboard_state["liveness_progress"] = 0
    dashboard_state["liveness_required"] = (
        challenge_manager.confirm_frames
    )
    dashboard_state["liveness_remaining"] = 0
    dashboard_state["liveness_message"] = message


def update_liveness_dashboard(result):
    dashboard_state["liveness_state"] = result["state"]
    dashboard_state["liveness_instruction"] = (
        result["instruction"]
    )
    dashboard_state["liveness_direction"] = (
        result["direction"]
    )
    dashboard_state["liveness_progress"] = (
        result["match_count"]
    )
    dashboard_state["liveness_required"] = (
        result["confirm_frames"]
    )
    dashboard_state["liveness_remaining"] = (
        result["remaining"]
    )
    dashboard_state["liveness_message"] = (
        result["message"]
    )


def generate_frames():

    print("[INFO] generate_frames() dimulai")

    # Cegah lebih dari satu stream memproses recognition.
    stream_acquired = recognition_stream_lock.acquire(
        blocking=False
    )

    if not stream_acquired:
        print(
            "[WARNING] Stream recognition lain masih aktif. "
            "Koneksi video kedua ditolak."
        )
        return

    prev_time = time.time()

    frame_count = 0
    cached_result = None
    cached_faces = None

    # Challenge khusus untuk satu sesi video.
    session_challenge = ChallengeManager()

    # Identitas yang sedang mengerjakan liveness.
    locked_person_id = None

    # Setelah absensi berhasil, tunggu wajah keluar
    # sebelum membuka sesi absensi baru.
    attendance_locked = False
    no_face_frames = 0
    release_face_frames = 8

    target_fps = 15
    frame_delay = 1 / target_fps
    detect_interval = 10

    try:

        while camera_manager.is_running():

            loop_start = time.time()
            frame_count += 1

            success, frame = camera_manager.read()

            if (
                not success
                or frame is None
                or not camera_manager.is_running()
            ):
                dashboard_state["camera"] = False
                break

            # ==========================
            # Update status kamera
            # ==========================
            dashboard_state["camera"] = True

            # Saat liveness aktif, detector dijalankan setiap frame
            # agar landmark mengikuti gerakan kepala terbaru.
            should_detect = (
                cached_faces is None
                or locked_person_id is not None
                or attendance_locked
                or frame_count % detect_interval == 0
            )

            if should_detect:
                cached_faces = detector.detect(frame)

            faces = cached_faces

            if not camera_manager.is_running():
                break

            dashboard_state["face_count"] = (
                0 if faces is None else len(faces)
            )

            # ==========================
            # Tidak ada wajah
            # ==========================
            if faces is None or len(faces) == 0:

                cached_result = None
                cached_faces = None
                locked_person_id = None

                session_challenge.reset()
                
                if attendance_locked:

                    no_face_frames +=1

                    if no_face_frames >= release_face_frames:
                        attendance_locked = false
                        no_face_frames = 0
                else:
                   no_face_frames = 0

                reset_liveness_dashboard()

                dashboard_state["name"] = "-"
                dashboard_state["person_id"] = "-"
                dashboard_state["confidence"] = 0
                dashboard_state["status"] = "Menunggu"

            # ==========================
            # Lebih dari satu wajah
            # ==========================
            elif len(faces) > 1:

                cached_result = None
                cached_faces = None
                locked_person_id = None

                session_challenge.reset()

                reset_liveness_dashboard(
                    instruction=(
                        "Pastikan hanya satu wajah terlihat."
                    ),
                    message=(
                        "Terdeteksi lebih dari satu wajah."
                    )
                )

                dashboard_state["name"] = "-"
                dashboard_state["person_id"] = "-"
                dashboard_state["confidence"] = 0
                dashboard_state["status"] = "Banyak Wajah"

            # ==========================
            # Tepat satu wajah
            # ==========================
            
            else:

                no_face_frames = 0
                face = faces[0]

                crop = detector.crop_face(
                    frame,
                    face
                )

                if crop is None or crop.size == 0:
                    cached_result = None
                    locked_person_id = None
                    session_challenge.reset()
                    continue

                quality = FaceQuality.score(crop)
                result = None

                # Saat challenge berlangsung, recognition dilakukan
                # setiap frame untuk memastikan orang tidak berganti.
                should_recognize = (
                    cached_result is None
                    or locked_person_id is not None
                    or frame_count % RECOGNITION_INTERVAL == 0
                )

                if quality["score"] >= QUALITY_THRESHOLD:

                    if should_recognize:
                        cached_result = recognizer.recognize(
                            frame,
                            face
                        )

                    result = cached_result

                else:
                    cached_result = None

                # Landmark YuNet harus disimpan sebelum flatten.
                face_data = face.copy()
                flat_face = face.flatten()

                x = int(flat_face[0])
                y = int(flat_face[1])
                w = int(flat_face[2])
                h = int(flat_face[3])

                color = (0, 255, 255)
                label = "MENUNGGU"

                # ==========================
                # Wajah dikenali
                # ==========================
                if result is not None:

                    if not camera_manager.is_running():
                        break

                    person_id = result["person_id"]
                    attendance_type = get_attendance_mode()

                    dashboard_state["name"] = result["name"]
                    dashboard_state["person_id"] = person_id
                    dashboard_state["confidence"] = round(
                        result["score"] * 100,
                        2
                    )

                    # ==========================
                    # Mode belum dipilih
                    # ==========================
                    if attendance_type not in (
                        "Masuk",
                        "Pulang"
                    ):
                        cached_result = None
                        locked_person_id = None

                        session_challenge.reset()

                        reset_liveness_dashboard(
                            instruction=(
                                "Pilih mode Masuk atau Pulang."
                            ),
                            message=(
                                "Mode absensi belum dipilih."
                            )
                        )

                        dashboard_state["status"] = "Pilih Mode"

                        color = (0, 255, 255)
                        label = "PILIH MODE ABSENSI"

                    # ==========================
                    # Sudah absen
                    # ==========================
                    elif attendance_exists(
                        person_id,
                        attendance_type
                    ):
                        cached_result = None
                        locked_person_id = None

                        session_challenge.reset()

                        reset_liveness_dashboard(
                            instruction=(
                                "Absensi {} hari ini "
                                "sudah tercatat."
                            ).format(attendance_type),
                            message=(
                                "Tidak perlu mengulang "
                                "tantangan."
                            )
                        )

                        dashboard_state["status"] = (
                            "Sudah Absen {}".format(
                                attendance_type
                            )
                        )

                        color = (0, 255, 0)

                        label = (
                            "{} - SUDAH {}".format(
                                result["name"],
                                attendance_type.upper()
                            )
                        )

                    # ==========================
                    # Jalankan liveness
                    # ==========================
                    else:

                        # Kunci identitas pertama yang memulai
                        # challenge.
                        if locked_person_id is None:
                            locked_person_id = person_id

                        # Bila identitas hasil recognition berubah,
                        # challenge langsung dibatalkan.
                        if person_id != locked_person_id:

                            previous_person_id = (
                                locked_person_id
                            )

                            cached_result = None
                            cached_faces = None
                            locked_person_id = None

                            session_challenge.reset()

                            reset_liveness_dashboard(
                                instruction=(
                                    "Identitas berubah. "
                                    "Silakan ulangi verifikasi."
                                ),
                                message=(
                                    "Challenge dibatalkan. "
                                    "{} berubah menjadi {}."
                                ).format(
                                    previous_person_id,
                                    person_id
                                )
                            )

                            dashboard_state["name"] = "-"
                            dashboard_state["person_id"] = "-"
                            dashboard_state["confidence"] = 0
                            dashboard_state["status"] = (
                                "Identitas Berubah"
                            )

                            color = (0, 0, 255)
                            label = "IDENTITAS BERUBAH"

                        else:

                            liveness_result = (
                                session_challenge.process(
                                    face_data,
                                    locked_person_id
                                )
                            )

                            update_liveness_dashboard(
                                liveness_result
                            )

                            # ==========================
                            # Liveness berhasil
                            # ==========================
                            if liveness_result["passed"]:

                                if not camera_manager.is_running():
                                    break

                                challenge_person_id = (
                                    liveness_result.get(
                                        "person_id"
                                    )
                                )

                                result_person_id = (
                                    result.get("person_id")
                                )

                                # Pemeriksaan terakhir sebelum
                                # penyimpanan database.
                                identity_valid = (
                                    challenge_person_id
                                    == locked_person_id
                                    and result_person_id
                                    == locked_person_id
                                    and person_id
                                    == locked_person_id
                                )

                                if not identity_valid:

                                    cached_result = None
                                    cached_faces = None
                                    locked_person_id = None

                                    session_challenge.reset()

                                    reset_liveness_dashboard(
                                        instruction=(
                                            "Identitas tidak "
                                            "konsisten. Ulangi."
                                        ),
                                        message=(
                                            "Penyimpanan dibatalkan "
                                            "karena identitas berubah."
                                        )
                                    )

                                    dashboard_state["name"] = "-"
                                    dashboard_state[
                                        "person_id"
                                    ] = "-"
                                    dashboard_state[
                                        "confidence"
                                    ] = 0
                                    dashboard_state["status"] = (
                                        "Identitas Tidak Konsisten"
                                    )

                                    color = (0, 0, 255)
                                    label = (
                                        "IDENTITAS TIDAK KONSISTEN"
                                    )

                                else:

                                    saved = (
                                        attendance_manager.save(
                                            result,
                                            frame,
                                            attendance_type=(
                                                attendance_type
                                            )
                                        )
                                    )

                                    if saved:
                                        attendance_locked = True
                                        dashboard_state[
                                            "status"
                                        ] = (
                                            "Hadir - {}".format(
                                                attendance_type
                                            )
                                        )

                                        label = (
                                            "{} - {} OK".format(
                                                result["name"],
                                                attendance_type.upper()
                                            )
                                        )

                                    else:
                                        dashboard_state[
                                            "status"
                                        ] = (
                                            "Sudah Absen {}".format(
                                                attendance_type
                                            )
                                        )

                                        label = (
                                            "{} - SUDAH {}".format(
                                                result["name"],
                                                attendance_type.upper()
                                            )
                                        )

                                    color = (0, 255, 0)

                                    # Reset total setelah satu hasil.
                                    cached_result = None
                                    cached_faces = None
                                    locked_person_id = None

                                    session_challenge.reset()

                            # ==========================
                            # Liveness gagal
                            # ==========================
                            elif liveness_result["failed"]:

                                cached_result = None
                                cached_faces = None
                                locked_person_id = None

                                session_challenge.reset()

                                dashboard_state["status"] = (
                                    "Liveness Gagal"
                                )

                                color = (0, 0, 255)
                                label = "LIVENESS GAGAL"

                            # ==========================
                            # Liveness berlangsung
                            # ==========================
                            else:

                                dashboard_state["status"] = (
                                    "Verifikasi Liveness"
                                )

                                color = (255, 165, 0)

                                label = (
                                    "{} | {}/{}".format(
                                        liveness_result[
                                            "instruction"
                                        ],
                                        liveness_result[
                                            "match_count"
                                        ],
                                        liveness_result[
                                            "confirm_frames"
                                        ]
                                    )
                                )

                # ==========================
                # Unknown
                # ==========================
                elif quality["score"] >= QUALITY_THRESHOLD:

                    cached_result = None
                    cached_faces = None
                    locked_person_id = None

                    session_challenge.reset()

                    reset_liveness_dashboard(
                        instruction="Wajah belum dikenali.",
                        message="Identitas tidak ditemukan."
                    )

                    dashboard_state["name"] = "-"
                    dashboard_state["person_id"] = "-"
                    dashboard_state["confidence"] = 0
                    dashboard_state["status"] = "Unknown"

                    color = (0, 255, 255)
                    label = "UNKNOWN"

                # ==========================
                # Kualitas buruk
                # ==========================
                else:

                    cached_result = None
                    cached_faces = None
                    locked_person_id = None

                    session_challenge.reset()

                    reset_liveness_dashboard(
                        instruction="Perbaiki posisi wajah.",
                        message=(
                            "Kualitas wajah belum memenuhi "
                            "syarat."
                        )
                    )

                    dashboard_state["name"] = "-"
                    dashboard_state["person_id"] = "-"
                    dashboard_state["confidence"] = 0
                    dashboard_state["status"] = (
                        "Kualitas Buruk"
                    )

                    color = (0, 0, 255)
                    label = "BAD ({}%)".format(
                        quality["score"]
                    )

                # ==========================
                # Bounding box
                # ==========================
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    color,
                    2
                )

                text_y = max(20, y - 10)

                cv2.putText(
                    frame,
                    label,
                    (x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

            if not camera_manager.is_running():
                break

            # ==========================
            # FPS dashboard
            # ==========================
            current_time = time.time()

            fps = 1 / max(
                current_time - prev_time,
                0.001
            )

            prev_time = current_time

            dashboard_state["fps"] = round(fps, 1)
            dashboard_state["last_update"] = current_time

            # ==========================
            # Encode frame
            # ==========================
            display_frame = cv2.resize(
                frame,
                (640, 480)
            )

            encode_success, buffer = cv2.imencode(
                ".jpg",
                display_frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    50
                ]
            )

            if not encode_success:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

            # ==========================
            # FPS limit
            # ==========================
            elapsed = time.time() - loop_start

            if elapsed < frame_delay:
                time.sleep(
                    frame_delay - elapsed
                )

    finally:

        # ==========================
        # Reset saat stream berhenti
        # ==========================
        dashboard_state["camera"] = False
        dashboard_state["face_count"] = 0
        dashboard_state["name"] = "-"
        dashboard_state["person_id"] = "-"
        dashboard_state["confidence"] = 0
        dashboard_state["status"] = "Offline"

        session_challenge.reset()

        reset_liveness_dashboard(
            instruction="Kamera tidak aktif.",
            message="Liveness dihentikan."
        )

        recognition_stream_lock.release()

        print("[INFO] generate_frames() selesai")


def reload_embeddings():
    """
    Memuat ulang embeddings.pkl tanpa restart kamera.
    """
    recognizer.load_embeddings()
    print("[INFO] Embeddings berhasil dimuat ulang.")

def generate_dataset_frames():
    """
    Stream khusus tambah/edit dataset.

    Tidak menjalankan:
    - face recognition
    - liveness
    - pengecekan absensi
    - penyimpanan absensi
    """

    print("[INFO] generate_dataset_frames() dimulai")

    target_fps = 15
    frame_delay = 1 / target_fps

    while camera_manager.is_running():

        loop_start = time.time()

        success, frame = camera_manager.read()

        if (
            not success
            or frame is None
            or not camera_manager.is_running()
        ):
            break

        try:
            faces = detector.detect(frame)
        except Exception:
            faces = None

        if faces is None or len(faces) == 0:

            cv2.putText(
                frame,
                "ARAHKAN SATU WAJAH KE KAMERA",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

        elif len(faces) > 1:

            cv2.putText(
                frame,
                "LEBIH DARI SATU WAJAH",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

            for face in faces:
                flat_face = face.flatten()

                x = int(flat_face[0])
                y = int(flat_face[1])
                w = int(flat_face[2])
                h = int(flat_face[3])

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

        else:

            face = faces[0]
            flat_face = face.flatten()

            x = int(flat_face[0])
            y = int(flat_face[1])
            w = int(flat_face[2])
            h = int(flat_face[3])

            crop = detector.crop_face(
                frame,
                face
            )

            if crop is not None and crop.size > 0:
                quality = FaceQuality.score(crop)
                quality_score = quality["score"]
            else:
                quality_score = 0

            if quality_score >= QUALITY_THRESHOLD:
                color = (0, 255, 0)
                label = "WAJAH SIAP - {}%".format(
                    quality_score
                )
            else:
                color = (0, 0, 255)
                label = "PERBAIKI POSISI - {}%".format(
                    quality_score
                )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                2
            )

            cv2.putText(
                frame,
                label,
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        display_frame = cv2.resize(
            frame,
            (640, 480)
        )

        encode_success, buffer = cv2.imencode(
            ".jpg",
            display_frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                50
            ]
        )

        if not encode_success:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )

        elapsed = time.time() - loop_start

        if elapsed < frame_delay:
            time.sleep(
                frame_delay - elapsed
            )
