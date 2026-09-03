import os
import cv2
import pickle

from database.database import get_person
from config import RECOGNITION_THRESHOLD

class FaceRecognizer:

    def __init__(self, model_path):

        self.recognizer = cv2.FaceRecognizerSF.create(
            model=model_path,
            config=""
        )

        self.embeddings = []
        self.embeddings_mtime = 0

        self.load_embeddings()

    def load_embeddings(self):

        try:

            with open(
                "models/embeddings/embeddings.pkl",
                "rb"
            ) as f:

                self.embeddings = pickle.load(f)

                try:
                    self.embeddings_mtime = os.path.getmtime(
                         "models/embeddings/embeddings.pkl"
                    )
                except OSError:
                    self.embeddings_mtime = 0

            self.embeddings_mtime = os.path.getmtime(
                "models/embeddings/embeddings.pkl"
            )
            print(f"[INFO] {len(self.embeddings)} embeddings loaded")

        except Exception as e:

            print("[ERROR] gagal membaca embeddings.pkl")

            print(e)

            self.embeddings = []

    def reload_if_changed(self):

        path = "models/embeddings/embeddings.pkl"

        try:
            mtime = os.path.getmtime(path)

            if mtime != self.embeddings_mtime:

                self.load_embeddings()
                self.embeddings_mtime = mtime

                print("[INFO] Embeddings berubah, dimuat ulang.")

        except OSError:
            pass

    def extract(self, image, face):

        aligned = self.recognizer.alignCrop(image, face)

        feature = self.recognizer.feature(aligned)

        return feature

    def match(self, feature1, feature2):

        return self.recognizer.match(
            feature1,
            feature2,
            cv2.FaceRecognizerSF_FR_COSINE
        )

    def recognize(
	self, 
	image, 
	face, 
	threshold=RECOGNITION_THRESHOLD
    ):

        self.reload_if_changed()

        feature = self.extract(image, face)

        scores_by_person = {}

        for item in self.embeddings:

            score = self.match(
                feature,
                item["embedding"]
            )

            person_id = item["person_id"]

            if person_id not in scores_by_person:
                scores_by_person[person_id] = []

            scores_by_person[person_id].append(
                float(score)
            )

        if not scores_by_person:
            return None

        best_person_id = None
        best_score = -1

        TOP_K = 3

        for person_id, scores in scores_by_person.items():

            scores = sorted(
                scores,
                reverse=True
            )

            top_scores = scores[:TOP_K]

            person_score = (
                sum(top_scores) /
                len(top_scores)
            )

            if person_score > best_score:
                best_score = person_score
                best_person_id = person_id

        print(
            "[MATCH]",
            best_person_id,
            "score:",
            round(best_score, 4)
        )

        if best_score < threshold:
            return None

        person = get_person(best_person_id)

        if person is None:

            return None

        return {

            "person_id": person["person_id"],

            "name": person["name"],

            "score": float(best_score)

        }
