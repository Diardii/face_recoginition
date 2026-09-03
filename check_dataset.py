import os

from training.embedding_generator import EmbeddingGenerator


generator = EmbeddingGenerator()

dataset_root = "dataset"

total = 0
valid = 0
failed = 0

for person_id in sorted(os.listdir(dataset_root)):

    person_folder = os.path.join(
        dataset_root,
        person_id
    )

    if not os.path.isdir(person_folder):
        continue

    print("\n=== {} ===".format(person_id))

    for filename in sorted(os.listdir(person_folder)):

        if not filename.lower().endswith(".jpg"):
            continue

        total += 1

        image_path = os.path.join(
            person_folder,
            filename
        )

        embedding = generator.generate(
            image_path
        )

        if embedding is None:
            failed += 1
            print(
                "[DITOLAK] {}".format(
                    image_path
                )
            )
        else:
            valid += 1


print("\n============================")
print("TOTAL :", total)
print("VALID :", valid)
print("GAGAL :", failed)
print("============================")
