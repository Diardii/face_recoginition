import threading

from training.train import train_all


class TrainingManager:

    def __init__(self):
        self.is_training = False
        self.progress = 0
        self.status = "Idle"
        self.last_result = None
        self.last_error = None
        self._lock = threading.Lock()

    def start(self):

        with self._lock:

            if self.is_training:
                return False

            self.is_training = True
            self.progress = 0
            self.status = "Preparing Training..."
            self.last_result = None
            self.last_error = None

        thread = threading.Thread(
            target=self.run_training,
            daemon=True
        )

        thread.start()

        return True

    def run_training(self):

        try:

            def update_progress(value):
                self.progress = max(0, min(100, int(value)))

            def update_status(text):
                self.status = str(text)

            result = train_all(
                progress_callback=update_progress,
                status_callback=update_status
            )

            # Reload hanya setelah file embeddings berhasil disimpan.
            from recognition.stream import reload_embeddings

            reload_embeddings()

            self.last_result = result
            self.progress = 100

            self.status = (
                "Finished - {} berhasil, {} gagal, "
                "{} total dataset".format(
                    result["success"],
                    result["failed"],
                    result["total"]
                )
            )

        except Exception as error:

            self.last_error = str(error)
            self.status = "Error: {}".format(error)

            print("[TRAINING ERROR] {}".format(error))

        finally:

            with self._lock:
                self.is_training = False


training_manager = TrainingManager()
