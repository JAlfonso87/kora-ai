import logging

from app.loaders.document_loader import DocumentLoader
from app.processors.document_processor import DocumentProcessor
from app.chunkers.document_chunker import DocumentChunker
from app.embeddings.embedding_generator import EmbeddingGenerator
from app.loaders.embedding_loader import EMBLoader

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self):
        self.embedding_loader = EMBLoader()
        self.loader = DocumentLoader()
        self.processor = DocumentProcessor()
        self.chunker = DocumentChunker()
        self.embedding_generator = EmbeddingGenerator()

    def ingest(self, file_path: str) -> dict:
        # Load the document and retrieve its metadata.
        print(f"<< STARTING FILE LOADING WITH PATH: {file_path} >>")
        document = self.loader.load(file_path)
        print("<< FILE LOADED SUCCESFULLY >>")

        # Normalize the extracted text.
        print(f"<< STARTING FILE PROCESSING... >>")
        processed_content = self.processor.process(
            document["content"]
        )
        print("<< FILE PROCESSED SUCCESSFULLY >>")

        # Split the normalized text into chunks.
        print("<< STARTING FILE CHUNKING... >>")
        chunks = self.chunker.split(processed_content)
        print("<< FILE CHUNKING FINISHED SUCCESSFULLY >>")

        print("<< RETRIEVED CHUNKS: >>")
        print(chunks)

        # Generate on embedding for each chunk
        print("<< STARTING CHUNK-EMBEDDING ASSIGNATION... >>")
        chunks_with_embedding = [
            {
                "chunk": chunk,
                "embedding": self.embedding_generator.generate(chunk)
            }
            for chunk in chunks
        ]
        print("<< CHUNK-EMBEDDING ASSIGNATION FINISHED SUCCESFULLY >>")

        # Return the chunks together with their source metadata.
        rfu = {
            "chunks": chunks_with_embedding,
            "metadata": document["metadata"]
        }  # "Ready For Upload"

        try:
            self.embedding_loader.upload(rfu)
        except Exception:
            logger.exception("Failed to persist ingestion data")
            raise

        return rfu
