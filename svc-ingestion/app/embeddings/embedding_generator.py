from sentence_transformers import SentenceTransformer
import logging, time

class EmbeddingGenerator:
    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    def __init__(self):
        # Load the multilingual embedding model.
        logger = logging.getLogger(__name__)

        start = time.perf_counter()

        logger.info("Iniciando carga del modelo: %s", self.MODEL_NAME)

        self.model = SentenceTransformer(self.MODEL_NAME)

        elapsed = time.perf_counter() - start

        logger.info(
            "Modelo cargado correctamente en %.2f segundos",
            elapsed,
        )

    def generate(self, text: str) -> list[float]:
        if not isinstance(text,  str):
            raise TypeError("Text must be a string")

        if not text.strip():
            raise ValueError("Text cannot be empty")

        # Convert the text into a normalized embedding vector.
        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def generate_batch(self, texts: list[str]) -> list[list[float]]:
        if not isinstance(texts, list):
            raise TypeError("Texts must be a list")

        if not texts:
            return []

        if any(not isinstance or not text.strip() for text in texts):
            raise ValueError("Texts must contain non-empty strings")

        # Generate embeddings for multiple text chunks at once.
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()