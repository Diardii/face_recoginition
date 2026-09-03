import uuid
from flask import Flask, render_template
import os
import base64
import shutil
import numpy as np
from training.train import train_all
from recognition.stream import reload_embeddings
from recognition.dashboard_state import dashboard_state
from recognition.dashboard_state import dashboard_state
from recognition.attendance_state import (
    set_attendance_mode,
    get_attendance_mode
)
from recognition.detect import FaceDetector
from training.trainer import training_manager
from recognition.recognize import FaceRecognizer
from config import SFACE_MODEL_PATH
from recognition.liveness.challenge_manager import ChallengeManager
from recognition.attendance_manager import AttendanceManager
import base64
import cv2
from recognition.camera import camera_manager
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    send_from_directory,
    Response,
    session
)

from database.database import (
    init_db,
    save_person,
    get_all_persons,
    generate_person_id,
    get_person,
    delete_person,
    update_dataset_count,
    update_person,
    delete_person,
    get_all_attendance,
    save_attendance,
    get_training_data,
    get_user_by_username,
    get_db,
    attendance_exists,
    verify_user_password
)

from recognition.stream import (
    generate_frames,
    generate_dataset_frames,
    camera_manager
)

from config import (
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    FLASK_THREADED,
    YUNET_MODEL_PATH
)

from training.dataset_validator import DatasetValidator

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

dataset_validator = DatasetValidator()

from functools import wraps

mobile_face_detector = FaceDetector(
    str(YUNET_MODEL_PATH)
)

mobile_face_recognizer = FaceRecognizer(
    str(SFACE_MODEL_PATH)
)

mobile_attendance_manager = AttendanceManager()

mobile_dataset_validator = DatasetValidator()

mobile_liveness_sessions = {}

def json_safe(value):
    if isinstance(value, dict):
        return {
            key: json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper



def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )


        if session.get("role") != "admin":

            return "Akses ditolak", 403


        return func(*args, **kwargs)

    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    username = request.form.get(
        "username"
    )

    password = request.form.get(
        "password"
    )


    user = get_user_by_username(
        username
    )


    if user and verify_user_password(
        user,
        password
    ):

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["person_id"] = user["person_id"]


        if user["role"] == "admin":

            return redirect(
                url_for("dashboard")
            )

        else:

            return redirect(
                url_for("employee_home")
            )


    return render_template(
        "login.html",
        error="Username atau password salah."
    )

@app.route("/employee")
@login_required
def employee_home():

    if session.get("role") != "employee":
        return "Akses ditolak", 403
    person_id = session.get("person_id")

    if not person_id:
        return "Akun belum terhubung dengan data person", 400
    person = get_person(person_id)

    if not person:
        return "Data person tidak ditemunkan", 404

    return render_template(
        "employee/home.html",
        person=person
    )

@app.route("/employee/register-face")
@login_required
def employee_register_face():

    if session.get("role") != "employee":
        return "Akses ditolak", 403

    person_id = session.get("person_id")

    if not person_id:
        return "Akun belum terhubung dengan person", 400

    person = get_person(person_id)

    if not person:
        return "Data person tidak ditemukan", 404

    return render_template(
        "employee/register_face.html",
        person=person
    )

@app.route("/employee/register-face/capture", methods=["POST"])
@login_required
def employee_register_face_capture():

    if session.get("role") != "employee":
        return jsonify({
            "status": "error",
            "message": "Akses ditolak"
        }), 403

    person_id = session.get("person_id")

    if not person_id:
        return jsonify({
            "status": "error",
            "message": "Akun belum terhubung dengan person"
        }), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Data tidak ditemukan"
        }), 400

    image_data = data.get("image")

    if not image_data:
        return jsonify({
            "status": "error",
            "message": "Foto tidak ditemukan"
        }), 400

    try:
        header, encoded = image_data.split(",", 1)

        image_bytes = base64.b64decode(encoded)

        np_arr = np.frombuffer(
            image_bytes,
            np.uint8
        )

        image = cv2.imdecode(
            np_arr,
            cv2.IMREAD_COLOR
        )

    except Exception as error:
        print("[REGISTER FACE DECODE ERROR]", error)

        return jsonify({
            "status": "error",
            "message": "Foto tidak valid"
        }), 400

    if image is None:
        return jsonify({
            "status": "error",
            "message": "Foto gagal dibaca"
        }), 400

    validation = mobile_dataset_validator.validate(
        image
    )

    if not validation["valid"]:
        return jsonify({
            "status": "continue",
            "message": validation["message"]
        })

    dataset_dir = os.path.join(
        "dataset",
        person_id
    )

    os.makedirs(
        dataset_dir,
        exist_ok=True
    )

    existing_images = [
        name
        for name in os.listdir(dataset_dir)
        if name.lower().endswith(".jpg")
    ]

    dataset_count = len(existing_images)

    target_dataset = 20

    if dataset_count >= target_dataset:

        update_dataset_count(
            person_id
        )

        training_started = (
            training_manager.start()
        )

        print(
            "[MOBILE REGISTER COMPLETE]",
            "person_id=", person_id,
            "dataset_count=", dataset_count,
            "training_started=", training_started
        )

        return jsonify({
            "status": "complete",
            "message": "Dataset sudah lengkap",
            "count": dataset_count,
            "target": target_dataset
        })

    filename = "{}_{:03d}.jpg".format(
        person_id,
        dataset_count + 1
    )

    image_path = os.path.join(
        dataset_dir,
        filename
    )

    saved = cv2.imwrite(
        image_path,
        image
    )

    if not saved:
        return jsonify({
            "status": "error",
            "message": "Gagal menyimpan dataset"
        }), 500

    dataset_count += 1

    print(
        "[REGISTER FACE]",
        "person_id=", person_id,
        "saved=", image_path,
        "count=", dataset_count
    )

    if dataset_count >= target_dataset:
        return jsonify({
            "status": "complete",
            "message": "Dataset lengkap: {}/{}".format(
                dataset_count,
                target_dataset
            ),
            "count": dataset_count,
            "target": target_dataset
        })

    return jsonify({
        "status": "continue",
        "message": "Dataset tersimpan: {}/{}".format(
            dataset_count,
            target_dataset
        ),
        "count": dataset_count,
        "target": target_dataset
    })

@app.route("/employee/attendance/capture", methods=["POST"])
@login_required
def employee_attendance_capture():

    if session.get("role") != "employee":
        return jsonify({
            "status": "error",
            "message": "Akses ditolak"
        }), 403

    person_id = session.get("person_id")

    if not person_id:
        return jsonify({
            "status": "error",
            "message": "Akun belum terhubung dengan person"
        }), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "status": "error",
            "message": "Data tidak ditemukan"
        }), 400

    image_data = data.get("image")
    attendance_type = data.get("attendance_type")

    if attendance_type not in ("masuk", "pulang"):
        return jsonify({
            "status": "error",
            "message": "Tipe absensi tidak valid"
        }), 400

    if not image_data:
        return jsonify({
            "status": "error",
            "message": "Foto tidak ditemukan"
        }), 400

    attendance_label = {
        "masuk": "Masuk",
        "pulang": "Pulang"
    }[attendance_type]
    
    if attendance_exists(
        person_id=person_id,
        attendance_type=attendance_label
    ):
        return jsonify({
            "status": "error",
            "message": "Anda sudah absen {} hari ini".format(
                attendance_label
            )
        }), 409

    try:
        header, encoded = image_data.split(",", 1)

        image_bytes = base64.b64decode(encoded)

        np_arr = np.frombuffer(
            image_bytes,
            np.uint8
        )

        image = cv2.imdecode(
            np_arr,
            cv2.IMREAD_COLOR
        )

    except Exception as error:
        print ("[MOBILE CAPTURE DECODE ERROR]", error)

        return jsonify({
            "status": "error",
            "massage": "foto tidak valid"
        }), 400

    if image is None:
        return jsonify({
            "status": "error",
            "message": "Foto gagal dibaca"
        }), 400

    faces = mobile_face_detector.detect(image)

    if faces is None or len(faces) == 0:
        return jsonify({
            "status": "error",
            "message": "Wajah tidak terdeteksi"
        }), 400

    if len(faces) != 1:
        return jsonify({
            "status": "error",
            "message": "Pastikan hanya satu wajah di kamera"
        }), 400

    face = faces[0]

    result = mobile_face_recognizer.recognize(
        image,
        face
    )

    if result is None:
        return jsonify({
            "status": "error",
            "message": "Wajah tidak dikenali"
    }), 400

    if result["person_id"] != person_id:
        print(
            "[MOBILE IDENTITY MISMATCH]",
            "login=", person_id,
            "recognized=", result["person_id"],
            "score=", result["score"]
        )

        return jsonify({
            "status": "error",
            "message": "Wajah tidak sesuai dengan akun yang login"
        }), 403

    liveness_session_id = session.get(
        "mobile_liveness_id"
    )

    if not liveness_session_id:
        liveness_session_id = str(uuid.uuid4())

        session["mobile_liveness_id"] = (
            liveness_session_id
        )


    challenge = mobile_liveness_sessions.get(
        liveness_session_id
    )

    if challenge is None:
        challenge = ChallengeManager()

        mobile_liveness_sessions[
            liveness_session_id
        ] = challenge


    liveness_result = challenge.process(
        face,
        person_id
    )

    print(
        "[MOBILE LIVENESS]",
        "person_id=", person_id,
        "state=", liveness_result["state"],
        "challenge=", liveness_result["challenge"],
        "direction=", liveness_result["direction"],
        "progress=",
        "{}/{}".format(
            liveness_result["match_count"],
            liveness_result["confirm_frames"]
        )
    )

    if liveness_result["failed"]:

        challenge.reset ()

        mobile_liveness_sessions.pop(
            liveness_session_id,
            None
        )

        session.pop(
            "mobile_liveness_id",
            None
        )

        return jsonify({
            "status": "error",
            "massage": "liveness gagal. silahkan ulangi.",
            "liveness": liveness_result
        }), 400

    if liveness_result["passed"]:

        saved = mobile_attendance_manager.save(
            result,
            image,
            attendance_type=attendance_label
        )

        challenge.reset()

        mobile_liveness_sessions.pop(
            liveness_session_id,
            None
        )

        session.pop(
            "mobile_liveness_id",
            None
        )

        if not saved:
            return jsonify({
                "status": "error",
                "message": "Absensi tidak dapat disimpan"
            }), 409

        print(
            "[MOBILE ATTENDANCE]",
            "person_id=", person_id,
            "type=", attendance_label,
            "score=", result["score"]
        )

        return jsonify({
            "status": "success",
            "message": "Absen {} berhasil".format(
                 attendance_label
            ),
            "attendance_type": attendance_label,
            "person_id": result["person_id"],
            "name": result["name"],
            "score": result["score"]
        })

    print(
        "[MOBILE RECOGNITION]",
        "login=", person_id,
        "recognized=", result["person_id"],
        "name=", result["name"],
        "score=", result["score"]
    )

    return jsonify ({
        "status": "continue",
        "message": liveness_result["instruction"],
        "liveness": liveness_result
    })


@app.route("/employee/history")
@login_required
def employee_history():

    if session.get("role") != "employee":
        return "Akses ditolak", 403

    person_id = session.get("person_id")

    if not person_id:
        return "Akun belum terhubung dengan person", 400

    conn = get_db()

    rows = conn.execute(
        """
        SELECT
            attendance_date,
            attendance_time,
            attendance_type,
            confidence
        FROM attendance
        WHERE person_id = ?
        ORDER BY attendance_date DESC, attendance_time DESC
        """,
        (person_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "employee/history.html",
        attendance=rows
    )

@app.route("/employee/attendance/<attendance_type>")
@login_required
def employee_attendance(attendance_type):

    if session.get("role") != "employee":
        return "Akses ditolak", 403

    if attendance_type not in ("masuk", "pulang"):
        return "Tipe absensi tidak valid", 400

    person_id = session.get("person_id")

    if not person_id:
        return "Akun belum terhubung dengan person", 400

    person = get_person(person_id)

    if not person:
        return "Data person tidak ditemukan", 404

    return render_template(
        "employee/attendance.html",
        person=person,
        attendance_type=attendance_type
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )

@app.route("/persons/delete/<person_id>", methods=["POST"])
@admin_required
def delete_person_route(person_id):

    try:

        # Hapus folder dataset
        folder = os.path.join("dataset", person_id)

        if os.path.exists(folder):

            shutil.rmtree(folder)

        # Hapus database
        delete_person(person_id)

        # Training ulang
        train_all()

        reload_embeddings()

        return jsonify({

            "status":"success"

        })

    except Exception as e:

        return jsonify({

            "status":"error",

            "message":str(e)

        })

@app.route("/camera/capture")
def camera_capture():

    frame = camera_manager.get_frame()

    if frame is None:

        return jsonify({

            "status":"error",

            "message":"Camera belum aktif."

        })

    success, buffer = cv2.imencode(".jpg", frame)

    if not success:

        return jsonify({

            "status":"error",

            "message":"Encode gagal."

        })

    image = base64.b64encode(buffer).decode()

    return jsonify({

        "status":"success",

        "photo":"data:image/jpeg;base64,"+image

    })
@app.route("/attendance/mode", methods=["GET", "POST"])
def attendance_mode():

    if request.method == "GET":

        return jsonify({
            "success": True,
            "attendance_type": get_attendance_mode()
        })

    data = request.get_json(silent=True) or {}

    attendance_type = data.get("attendance_type")

    success = set_attendance_mode(
        attendance_type
    )

    if not success:

        return jsonify({
            "success": False,
            "message": (
                "Jenis absensi harus Masuk atau Pulang."
            )
        }), 400

    return jsonify({
        "success": True,
        "attendance_type": attendance_type,
        "message": (
            "Mode absensi berhasil diubah menjadi "
            + attendance_type
            + "."
        )
    })
@app.route("/camera/start", methods=["POST"])
def camera_start():

    success = camera_manager.start()

    if not success:
        return jsonify({
            "success": False,
	    "status": "error",
            "message": "Camera gagal dibuka."
        })

    return jsonify({
        "success": True,
	"status": "success",
	"message": "camera berhasil dibuka."
    })
@app.route("/api/train/status")
def training_status():

    return jsonify({

        "running": training_manager.is_training,

        "progress": training_manager.progress,

        "status": training_manager.status

    })
@app.route("/api/train/start", methods=["POST"])
def start_training():

    success = training_manager.start()

    return jsonify({

        "success": success

    })
@app.route("/camera/stop", methods=["POST"])
def camera_stop():

    camera_manager.stop()

    return jsonify({
        "success": True
    })
@app.route("/persons/new")
def person_add():

    return render_template("person_add.html")
@app.route("/")
def index():
    return redirect(url_for("dashboard"))
@app.route("/person/<person_id>", methods=["DELETE"])
def remove_person(person_id):

    folder = os.path.join("dataset", person_id)

    if os.path.exists(folder):
        shutil.rmtree(folder)

    delete_person(person_id)

    return jsonify({
        "status": "success",
        "message": "Person berhasil dihapus."
    })
@app.route("/train")
def train():

    persons = get_training_data()

    return render_template(
        "train.html",
        persons=persons
    )
@app.route("/camera")
def camera():
    return render_template("camera.html")
from recognition.stream import generate_frames
@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
@app.route("/dataset_video_feed")
def dataset_video_feed():
    return Response(
        generate_dataset_frames(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )
@app.route("/recognition/status")
def recognition_status():

    return jsonify(dashboard_state)
@app.route("/dataset/<person_id>/<filename>")
def dataset_image(person_id, filename):

    folder = os.path.join("dataset", person_id)

    return send_from_directory(folder, filename)
@app.route("/person/<person_id>/dataset")
def get_dataset(person_id):

    folder = os.path.join("dataset", person_id)

    if not os.path.exists(folder):

        return jsonify({
            "status":"success",
            "images":[]
        })

    images = []

    for file in sorted(os.listdir(folder)):

        if file.lower().endswith((".jpg",".jpeg",".png")):

            images.append(file)

    return jsonify({

        "status":"success",

        "images":images

    })

@app.route(
    "/person/<person_id>/dataset/add",
    methods=["POST"]
)
def add_dataset(person_id):

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "Data permintaan tidak valid."
            }), 400

        photo = data.get("photo")

        if not photo:
            return jsonify({
                "status": "error",
                "message": "Foto tidak ditemukan."
            }), 400

        if not isinstance(photo, str):
            return jsonify({
                "status": "error",
                "message": "Format foto tidak valid."
            }), 400

        if "," not in photo:
            return jsonify({
                "status": "error",
                "message": "Format Base64 foto tidak valid."
            }), 400

        header, image_data = photo.split(",", 1)

        if not header.startswith("data:image/"):
            return jsonify({
                "status": "error",
                "message": "Data yang dikirim bukan gambar."
            }), 400

        try:
            decoded = base64.b64decode(
                image_data,
                validate=True
            )

        except Exception:
            return jsonify({
                "status": "error",
                "message": "Data Base64 foto rusak."
            }), 400

        if len(decoded) == 0:
            return jsonify({
                "status": "error",
                "message": "Data gambar kosong."
            }), 400

        image_array = np.frombuffer(
            decoded,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None or image.size == 0:
            return jsonify({
                "status": "error",
                "message": "Gambar tidak dapat dibaca."
            }), 400

        validation = dataset_validator.validate(image)

        if not validation["valid"]:

            quality = validation.get("quality")

            response = {
                "status": "error",
                "message": validation["message"]
            }

            if quality is not None:
                response["quality"] = json_safe(quality)

            return jsonify(response), 400

        folder = os.path.join(
            "dataset",
            person_id
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        files = [
            filename
            for filename in os.listdir(folder)
            if filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ]

        numbers = []

        for filename in files:

            stem = os.path.splitext(filename)[0]

            if stem.isdigit():
                numbers.append(int(stem))

        if numbers:
            next_number = max(numbers) + 1
        else:
            next_number = 1

        filename = "{:03d}.jpg".format(
            next_number
        )

        file_path = os.path.join(
            folder,
            filename
        )

        # Simpan gambar asli yang sudah lolos validasi.
        saved = cv2.imwrite(
            file_path,
            image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                95
            ]
        )

        if not saved:
            return jsonify({
                "status": "error",
                "message": "Gagal menyimpan gambar dataset."
            }), 500

        update_dataset_count(person_id)

        quality = validation.get("quality") or {}

        return jsonify({
            "status": "success",
            "message": "Foto dataset berhasil disimpan.",
            "filename": filename,
            "quality": quality
        })

    except Exception as error:

        print(
            "[DATASET] Gagal menambah dataset:",
            error
        )

        return jsonify({
            "status": "error",
            "message": (
                "Terjadi kesalahan saat memproses foto."
            )
        }), 500

@app.route("/person/<person_id>/update", methods=["POST"])
def update_person_route(person_id):

    data = request.get_json()

    update_person(

        person_id,

        data["name"],

        data["gender"],

        data["division"]

    )

    return jsonify({

        "status":"success"

    })
@app.route("/person/<person_id>/dataset/<filename>", methods=["DELETE"])
def delete_dataset_image(person_id, filename):

    file_path = os.path.join(
        "dataset",
        person_id,
        filename
    )

    if not os.path.exists(file_path):

        return jsonify({
            "status": "error",
            "message": "File tidak ditemukan."
        }), 404

    os.remove(file_path)

    # Update jumlah dataset di database
    update_dataset_count(person_id)

    return jsonify({
        "status": "success"
    })

@app.route("/save_person", methods=["POST"])
def save_person_route():

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "Data permintaan tidak valid."
            }), 400

        person_id = str(data.get("person_id", "")).strip()
        name = str(data.get("name", "")).strip()
        gender = str(data.get("gender", "")).strip()
        division = str(data.get("division", "")).strip()
        photos = data.get("photos", [])

        if not person_id:
            return jsonify({
                "status": "error",
                "message": "ID person belum tersedia."
            }), 400

        if not name:
            return jsonify({
                "status": "error",
                "message": "Nama belum diisi."
            }), 400

        if not isinstance(photos, list) or len(photos) == 0:
            return jsonify({
                "status": "error",
                "message": "Dataset masih kosong."
            }), 400

        validated_images = []

        # Validasi seluruh foto sebelum ada file yang disimpan.
        for index, photo in enumerate(photos):

            photo_number = index + 1

            if not isinstance(photo, str) or "," not in photo:
                return jsonify({
                    "status": "error",
                    "message": (
                        "Foto ke-{} memiliki format yang tidak valid."
                    ).format(photo_number)
                }), 400

            header, encoded = photo.split(",", 1)

            if not header.startswith("data:image/"):
                return jsonify({
                    "status": "error",
                    "message": (
                        "Foto ke-{} bukan data gambar."
                    ).format(photo_number)
                }), 400

            try:
                decoded = base64.b64decode(
                    encoded,
                    validate=True
                )
            except Exception:
                return jsonify({
                    "status": "error",
                    "message": (
                        "Data Base64 foto ke-{} rusak."
                    ).format(photo_number)
                }), 400

            if len(decoded) == 0:
                return jsonify({
                    "status": "error",
                    "message": (
                        "Foto ke-{} kosong."
                    ).format(photo_number)
                }), 400

            image_array = np.frombuffer(
                decoded,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None or image.size == 0:
                return jsonify({
                    "status": "error",
                    "message": (
                        "Foto ke-{} tidak dapat dibaca."
                    ).format(photo_number)
                }), 400

            validation = dataset_validator.validate(image)

            if not validation["valid"]:
                response = {
                    "status": "error",
                    "message": (
                        "Foto ke-{} ditolak: {}"
                    ).format(
                        photo_number,
                        validation["message"]
                    )
                }

                quality = validation.get("quality")

                if quality is not None:
                    response["quality"] = quality

                return jsonify(response), 400

            validated_images.append(image)

        # Semua foto sudah lolos validasi.
        folder = os.path.join(
            "dataset",
            person_id
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        saved_files = []

        for index, image in enumerate(validated_images):

            filename = "{:03d}.jpg".format(index + 1)

            file_path = os.path.join(
                folder,
                filename
            )

            saved = cv2.imwrite(
                file_path,
                image,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    95
                ]
            )

            if not saved:
                for saved_file in saved_files:
                    try:
                        os.remove(saved_file)
                    except Exception:
                        pass

                return jsonify({
                    "status": "error",
                    "message": (
                        "Gagal menyimpan foto dataset ke-{}."
                    ).format(index + 1)
                }), 500

            saved_files.append(file_path)

        save_person(
            person_id,
            name,
            gender,
            division,
            len(validated_images)
        )

        update_dataset_count(person_id)

        reload_embeddings()
        result = train_all()
        reload_embeddings()

        return jsonify({
            "status": "success",
            "message": "Person dan dataset berhasil disimpan.",
            "dataset_count": len(validated_images)
        })

    except Exception as error:

        print(
            "[SAVE PERSON] Gagal menyimpan person:",
            error
        )

        return jsonify({
            "status": "error",
            "message": (
                "Terjadi kesalahan saat menyimpan person: {}"
            ).format(error)
        }), 500

@app.route("/persons/<person_id>/edit")
def person_edit(person_id):

            person = get_person(person_id)

            if person is None:

                return "Person Not Found", 404

            return render_template(

                "person_edit.html",

                person=person

            )
@app.route("/person/<person_id>")
def person_detail(person_id):

    person = get_person(person_id)

    if person is None:
        return jsonify({
            "status": "error",
            "message": "Person tidak ditemukan"
        }), 404

    return jsonify({

        "status": "success",

        "person": {

            "person_id": person["person_id"],
            "name": person["name"],
            "gender": person["gender"],
            "division": person["division"],
            "dataset_count": person["dataset_count"],
            "status": person["status"],
            "created_at": person["created_at"]

        }

    })
# ==========================
# Dashboard
# ==========================
@app.route("/generate_person_id")
def get_person_id():

    person_id = generate_person_id()

    return jsonify({

        "person_id": person_id

    })
@app.route("/dashboard")
@admin_required
def dashboard():
    
    return render_template(
        "dashboard.html"
    )
# ==========================
# attendance
# ==========================
#@app.route("/attendance/save", methods=["POST"])
#def attendance_save():
#
#   data = request.get_json()
#
#    print("DATA DITERIMA:", data)
#
#    person_id = data.get("person_id")
#    person_name = data.get("person_name")
#    attendance_type = data.get("attendance_type")
#    confidence = data.get("confidence")
#    image = data.get("image")
#
#    save_attendance(
#        person_id,
#        person_name,
#        attendance_type,
#        confidence,
#        image
#    )
#
#    print("DATA BERHASIL DIKIRIM KE DATABASE")
#
#    return jsonify({
#        "success": True,
#        "message": "Absensi berhasil disimpan"
#    })
# ==========================
# Data Person
# ==========================
@app.route("/persons")
def persons():

    persons = get_all_persons()

    print(persons)

    return render_template(
        "persons.html",
        persons=persons
    )
# ==========================
# Tambah Person
# ==========================
@app.route("/persons/add")
def add_person():
    return render_template("add_person.html")

# ==========================
# Detail Person
# ==========================
@app.route("/persons/detail")
def detail_person():
    return render_template("detail_person.html")


# ==========================
# Riwayat
# ==========================
@app.route("/history")
def history():

    attendance = get_all_attendance()

    return render_template(
        "history.html",
        attendance=attendance
    )
# ==========================
# Pengaturan
# ==========================
@app.route("/setting")
def setting():
    return render_template("setting.html")

@app.route("/camera/list")
def camera_list():

    import cv2

    cameras = []

    for i in range(10):

        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        if cap.isOpened():

            ret, _ = cap.read()

            if ret:

                cameras.append({
                    "index": i,
                    "name": f"Camera {i}"
                })

            cap.release()

    return jsonify(cameras)
# ==========================
# Jalankan Flask
# ==========================
if __name__ == "__main__":
    init_db()
    app.run(
	host=FLASK_HOST,
	port=FLASK_PORT,
	debug=FLASK_DEBUG,
	threaded=FLASK_THREADED,
        ssl_context=(
            "cert/server.crt",
            "cert/server.key"
        )
)
 
