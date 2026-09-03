from pathlib import Path


class DatasetLoader:

    def __init__(self, dataset_path="dataset"):
        self.dataset_path = Path(dataset_path)

    def load(self):

        data = []

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Folder dataset tidak ditemukan: {self.dataset_path}"
            )

        for person_folder in sorted(self.dataset_path.iterdir()):

            if not person_folder.is_dir():
                continue

            person_id = person_folder.name

            for image_path in sorted(person_folder.glob("*.jpg")):

                data.append({
                    "person_id": person_id,
                    "image_path": str(image_path)
                })

        return data