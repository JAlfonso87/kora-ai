from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.pipeline.ingestion_pipeline import IngestionPipeline

app = FastAPI(
    title="Kora AI - Ingestion Service",
    version="1.0.0"
)

pipeline = IngestionPipeline()


class IngestionRequest(BaseModel):
    file_path: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_document(request: IngestionRequest):
    # Resolve the document path from the ingestion service directory.
    base_path = Path(__file__).resolve().parent.parent
    file_path = (base_path / request.file_path).resolve()

    # Prevent access to files outside the ingestion service directory.
    if not file_path.is_relative_to(base_path.resolve()):
        raise HTTPException(
            status_code=400,
            detail="File path is outside the ingestion directory"
        )

    try: 
        return pipeline.ingest(str(file_path))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )