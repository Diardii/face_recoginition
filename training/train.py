import os
import pickle

from training.dataset_loader import DatasetLoader
from training.embedding_generator import EmbeddingGenerator
from config import EMBEDDINGS_PATH, TEMP_EMBEDDINGS_PATH


def train_all(progress_callback=None, status_callback=None):

    loader = DatasetLoader()

    if status_callback:
        status_callback("Loading Dataset...")

    dataset = loader.load()
    total_dataset = len(dataset)

    if total_dataset == 0:
        raise RuntimeError("Dataset kosong. Training dibatalkan.")

    generator = EmbeddingGenerator()

    if status_callback:
        status_callback("Generating Embedding...")

    embeddings = []

    success = 0
    failed = 0

    for index, item in enumerate(dataset):

        try:
            embedding = generator.generate(item["image_path"])

            if embedding is None:
                print("[FAILED] {}".format(item["image_path"]))
                failed += 1
            else:
                embeddings.append({
                    "person_id": item["person_id"],
                    "image_path": item["image_path"],
                    "embedding": embedding
                })

                success += 1

                print("[OK] {}".format(item["image_path"]))

        except Exception as error:
            failed += 1

            print(
                "[TRAINING ERROR] {}: {}".format(
                    item["image_path"],
                    error
                )
            )

        finally:
            if progress_callback:
                progress = int(
                    ((index + 1) / total_dataset) * 90
                )
                progress_callback(progress)

    if success == 0:
        raise RuntimeError(
            "Tidak ada embedding yang berhasil dibuat. "
            "File embedding lama dipertahankan."
        )

    if status_callback:
        status_callback("Saving embeddings.pkl...")

    os.makedirs(
        str(EMBEDDINGS_PATH.parent),
        exist_ok=True
    )

    try:
        with open(str(TEMP_EMBEDDINGS_PATH), "wb") as file:
            pickle.dump(
                embeddings,
                file,
                protocol=pickle.HIGHEST_PROTOCOL
            )

        # Validasi file sementara sebelum mengganti file utama
        with open(str(TEMP_EMBEDDINGS_PATH), "rb") as file:
            loaded = pickle.load(file)

        if not isinstance(loaded, list):
            raise RuntimeError(
                "Format embedding sementara tidak valid."
            )

        os.replace(
            str(TEMP_EMBEDDINGS_PATH),
            str(EMBEDDINGS_PATH)
        )

    except Exception:

        if TEMP_EMBEDDINGS_PATH.exists():
            try:
                os.remove(str(TEMP_EMBEDDINGS_PATH))
            except OSError:
                pass

        raise

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Finished")

    return {
        "success": success,
        "failed": failed,
        "total": total_dataset
    }
