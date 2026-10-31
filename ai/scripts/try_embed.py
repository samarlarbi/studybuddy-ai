import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    cache_dir="./models_cache",
)

texts = [
    "Comment afficher une carte Leaflet ?",
    "Afficher la carte centrée sur la position GPS",
    "La recette du couscous au poisson",
]
vecs = np.array(list(model.embed(texts)))
print("shape:", vecs.shape)


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


print("question vs carte  :", round(cos(vecs[0], vecs[1]), 3))
print("question vs couscous:", round(cos(vecs[0], vecs[2]), 3))