import logging
import tempfile

from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.pipeline.ingestion_pipeline import IngestionPipeline
from app.embeddings.embedding_generator import EmbeddingGenerator
from app.search.search_document import SearchDocument

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kora AI - Ingestion Service",
    version="1.0.0",
)

pipeline = IngestionPipeline()
eg = EmbeddingGenerator()
sd = SearchDocument()


class IngestionRequest(BaseModel):
    file_path: str


class SearchQuery(BaseModel):
    content: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query")
def process_query(query: SearchQuery):
    user_query = query.content
    print(f"<< RECEIVED QUERY: {user_query}")
    embedded_query = eg.generate(user_query)
    query_results = sd.search(embedded_query)

    return query_results


@app.post("/ingest")
def ingest_document(request: IngestionRequest):
    # Resolve the document path from the ingestion service directory.
    base_path = Path(__file__).resolve().parent.parent
    file_path = (base_path / request.file_path).resolve()

    # Prevent access to files outside the ingestion service directory.
    if not file_path.is_relative_to(base_path):
        raise HTTPException(
            status_code=400,
            detail="File path is outside the ingestion directory"
        )

    try:
        logger.info("Starting ingestion for file: %s", file_path)
        ingestion_result = pipeline.ingest(str(file_path))
        logger.info("Ingestion completed successfully: %s", file_path)
        return ingestion_result

    except FileNotFoundError as error:
        logger.warning("Document not found: %s", file_path)
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        ) from error

    except ValueError as error:
        logger.warning("Invalid document or input: %s", error)
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        logger.exception("Unexpected error during document ingestion")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during document ingestion"
        ) from error


@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    # Validate the uploaded file type.
    allowed_extensions = {".pdf", ".txt"}
    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF and TXT are allowed."
        )

    # Save the uploaded file temporarily for ingestion.
    try:
        with tempfile.NamedTemporaryFile(
            suffix=file_extension,
            delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(file.file.read())

        # Process and persist the document using the existing pipeline.
        return pipeline.ingest(str(temporary_path))

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Uploaded document could not be processed."
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        logger.exception("Unexpected error during file upload")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during file upload."
        ) from error

    finally:
        if "temporary_path" in locals():
            temporary_path.unlink(missing_ok=True)
        file.file.close()
