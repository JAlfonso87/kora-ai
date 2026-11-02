import logging
import time

from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    MODEL_NAME = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    def __init__(self):
        logger = logging.getLogger(__name__)
        start = time.perf_counter()

        logger.info("Loading embedding model: %s", self.MODEL_NAME)

        self.model = SentenceTransformer(self.MODEL_NAME)

    def generate(self, text: str) -> list[float]:
        if not isinstance(text, str):
            raise TypeError("Text must be a string")

        if not text.strip():
            raise TypeError("Text cannot be empty")

        embedding = self.model.encode(
            text, normalize_embeddings=True
        )

        return embedding.tolist()
