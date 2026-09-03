import cv2
import threading
import platform

from config import (
    CAMERA_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FPS,
    CAMERA_SCAN_LIMIT
)

class CameraManager:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

                cls._instance.camera = None
                cls._instance.running = False

                # Webcam Jetson Anda berada di index 1
                cls._instance.camera_index = CAMERA_INDEX

                cls._instance.width = CAMERA_WIDTH
                cls._instance.height = CAMERA_HEIGHT
                cls._instance.fps = CAMERA_FPS

        return cls._instance

    # ==================================================
    # Cari kamera yang tersedia
    # ==================================================

    def get_available_cameras(self):

        cameras = []

        for index in range(CAMERA_SCAN_LIMIT):

            if platform.system() == "Windows":
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

            if cap.isOpened():

                ret, _ = cap.read()

                if ret:
                    cameras.append(index)

            cap.release()

        return cameras

    # ==================================================
    # Ganti kamera
    # ==================================================

    def set_camera_index(self, index):

        self.camera_index = int(index)

    # ==================================================
    # Start Camera
    # ==================================================

    def start(self):

        if self.running:

            return True

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        print(f"Membuka kamera index : {self.camera_index}")

        if platform.system() == "Windows":

            self.camera = cv2.VideoCapture(
                self.camera_index,
                cv2.CAP_DSHOW
            )

        else:

            self.camera = cv2.VideoCapture(
                self.camera_index,
                cv2.CAP_V4L2
            )

	# Optimasi buffer kamera
        self.camera.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )

        self.camera.set(
            cv2.CAP_PROP_FPS,
            15
        )

        # Jika gagal, cari kamera lain
        if not self.camera.isOpened():

            cameras = self.get_available_cameras()

            if len(cameras) == 0:

                print("Tidak ada kamera.")

                return False

            self.camera_index = cameras[0]

            print("Menggunakan kamera :", self.camera_index)

            if platform.system() == "Windows":

                self.camera = cv2.VideoCapture(
                    self.camera_index,
                    cv2.CAP_DSHOW
                )

            else:

                self.camera = cv2.VideoCapture(
                    self.camera_index,
                    cv2.CAP_V4L2
                )

        if not self.camera.isOpened():

            print("Gagal membuka kamera.")

            return False

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        self.camera.set(
            cv2.CAP_PROP_FPS,
            self.fps
        )

        self.running = True

        print("Camera opened :", self.camera.isOpened())
        print("Camera running :", self.running)

        return True

    # ==================================================
    # Stop Camera
    # ==================================================

    def stop(self):

        self.running = False

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        print("Camera stopped")

    # ==================================================
    # Status
    # ==================================================

    def is_running(self):

        return self.running

    # ==================================================
    # Read Frame
    # ==================================================
    def read(self):

        if self.camera is None:
            return False, None

        if not self.camera.isOpened():
            return False, None

        return self.camera.read()
    # ==================================================
    # Ambil 1 Frame
    # ==================================================

    def get_frame(self):

        print("===== GET FRAME =====")

        print("Running :", self.running)

        if self.camera is None:

            print("Camera None")

            return None

        if not self.camera.isOpened():

            print("Camera Closed")

            return None

        success, frame = self.camera.read()

        print("Read :", success)

        if not success:

            return None

        return frame.copy()

    # ==================================================
    # Release
    # ==================================================

    def release(self):

        self.stop()


camera_manager = CameraManager()
