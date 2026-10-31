import os
from functools import lru_cache

from fastembed import TextEmbedding

MODEL_NAME = os.environ.get(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)


@lru_cache(maxsize=1)
def get_model() -> TextEmbedding:
    return TextEmbedding(
        MODEL_NAME, cache_dir=os.environ.get("MODEL_CACHE_DIR", "./models_cache")
    )


def embed_texts(texts: list[str]):
    return list(get_model().embed(texts))