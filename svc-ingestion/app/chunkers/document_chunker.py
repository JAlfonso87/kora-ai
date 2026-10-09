class DocumentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "Overlap must be non-negative and smaller than chunk size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, content: str) -> list[str]:
        if not isinstance(content, str):
            raise TypeError("Document content must be a string")

        # Split the text into chunks wit a configurable overlap
        chunks = []
        start = 0
        step = self.chunk_size - self.overlap

        while start < len(content):
            end = start + self.chunk_size
            chunk = content[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += step

        return chunks
