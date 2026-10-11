from pathlib import Path

import fitz


class DocumentLoader:
    # File extensions supported by the ingestion service.
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt"
    }

    def load(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"unsopported document type: {path.suffix}"
            )

        # Select the appropriate loader according to the file type.
        if path.suffix.lower() == ".pdf":
            content = self._load_pdf(path)
        else:
            content = self._load_txt(path)

        # Keep the extracted content together with its source metadata
        return {
            "content": content,
            "metadata": {
                "source": path.name,
                "file_type": path.suffix.lower().replace(".", "")
            }
        }

    def _load_pdf(self, path: Path) -> str:
        # Open the PDF and extract text from each page.
        document = fitz.open(path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        return "\n".join(pages)

    def _load_txt(self, path: Path) -> str:
        # Read the text file using UTF-8 encoding.
        return path.read_text(encoding="utf-8")
