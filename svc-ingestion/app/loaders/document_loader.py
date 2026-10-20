from pathlib import Path

import fitz, os


class DocumentLoader:
    # File extensions supported by the ingestion service.
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt"
    }

    def load(self, file_path: str) -> dict:
        print(f"<< PATH RECEIVED IN document_loader.load: {file_path} >>")
        path = Path(file_path)

        print(f"<< STARTING FILE'S EXISTENCE EVALUATION FROM PATH: {file_path} >>")
        print(f"<< RESULT: {path.exists()} >>")
        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        print("<< STARTING FILE'S SUFFIX EVALUATION: >>")
        print(f"<< RESULT: {path.suffix.lower()}")
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"unsupported document type: {path.suffix}"
            )

        # Select the appropriate loader according to the file type.
        if path.suffix.lower() == ".pdf":
            content = self._load_pdf(path)
        else:
            content = self._load_txt(path)

        # Keep the extracted content together with its source metadata

        result = {
            "content": content,
            "metadata": {
                "file_name": path.stem,
                "mime_type": "text/plain" if path.suffix == ".txt" else "application/pdf",
                "source": path.name,
                "file_type": path.suffix.lower().replace(".", ""),
                "file_size": os.path.getsize(file_path)
            }
        }

        print("<< LOADING RESULT: >>")
        print(result)

        return result

    def _load_pdf(self, path: Path) -> str:
        print("<< LOAD ROUTE: .pdf >>")
        # Open the PDF and extract text from each page.
        document = fitz.open(path)

        pages = []

        for page in document:
            pages.append(page.get_text())

        document.close()

        return "\n".join(pages)

    def _load_txt(self, path: Path) -> str:
        print("<< LOAD ROUTE: .txt >>")
        # Read the text file using UTF-8 encoding.
        return path.read_text(encoding="utf-8")
