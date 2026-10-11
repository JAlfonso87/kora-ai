
import pytest

from app.pipeline.ingestion_pipeline import IngestionPipeline


def test_ingest_text_document():
    pipeline = IngestionPipeline()

    result = pipeline.ingest("test_data/nutrition_test.txt")

    assert len(result["chunks"]) > 0
    assert result["metadata"]["source"] == "nutrition_test.txt"
    assert result["metadata"]["file_type"] == "txt"

    for chunk in result["chunks"]:
        assert isinstance(chunk, dict)
        assert isinstance(chunk["text"], str)
        assert chunk["text"].strip() != ""

        assert isinstance(chunk["embedding"], list)
        assert len(chunk["embedding"]) == 384
        assert all(isinstance(value, float) for value in chunk["embedding"])


def test_ingest_nonexistent_document():
    pipeline = IngestionPipeline()

    with pytest.raises(FileNotFoundError):
        pipeline.ingest("test_data/nonexistent.txt")


def test_ingest_empty_document(tmp_path):
    pipeline = IngestionPipeline()
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    result = pipeline.ingest(str(empty_file))

    assert result["chunks"] == []
    assert result["metadata"]["source"] == "empty.txt"
    assert result["metadata"]["file_type"] == "txt"
