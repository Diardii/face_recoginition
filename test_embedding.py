from training.embedding_generator import EmbeddingGenerator

generator = EmbeddingGenerator()

embedding = generator.generate(
    "dataset/FR0001/001.jpg"
)

if embedding is None:
    print("Wajah tidak ditemukan")
else:
    print("Embedding berhasil dibuat")
    print("Shape :", embedding.shape)
    print(embedding)