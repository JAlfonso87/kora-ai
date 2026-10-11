from app.loaders.document_loader import DocumentLoader
from app.processors.document_processor import DocumentProcessor
from app.chunkers.document_chunker import DocumentChunker
from app.embeddings.embedding_generator import EmbeddingGenerator

class IngestionPipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.processor = DocumentProcessor()
        self.chunker = DocumentChunker()
        self.embedding_generator = EmbeddingGenerator()

    def ingest(self, file_path: str) -> dict:
        # Load the document and retrieve its metadata.
        document = self.loader.load(file_path)

        # Normalize the extracted text.
        processed_content = self.processor.process(
            document["content"]
        )

        # Split the normalized text into chunks.
        chunks = self.chunker.split(processed_content)

        # Generate on embedding for each chunk
        chunks_with_embedding = [
            {
                "text": chunk,
                "embedding": self.embedding_generator.generate(chunk)
            }
            for chunk in chunks
        ]

        # Return the chunks together with their source metadata.
        return {
            "chunks": chunks_with_embedding,
            "metadata": document["metadata"]
        }