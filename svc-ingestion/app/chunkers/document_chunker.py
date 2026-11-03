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
        print("<< CONTENT RECEIVED IN document_chunker.split: OK >>")
        if not isinstance(content, str):
            raise TypeError("Document content must be a string")

        # Split the text into chunks wit a configurable overlap
        chunks = []
        start = 0
        end = self.chunk_size
        step = self.chunk_size - self.overlap

        print("<< CALCULATED CHUNKING PARAMETERS FOR CURRENT ACTION: >>")
        print(f"<< START: {start} >>")
        print(f"<< END: {end} >>")
        print(f"<< STEP: {step} >>")

        while True:
            chunk = content[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end + 1 >= len(content):
                break

            start += step
            end = start + self.chunk_size

        print("<< CHUNKING CYCLE FINISHED WITH NO ERRORS >>")

        return chunks
