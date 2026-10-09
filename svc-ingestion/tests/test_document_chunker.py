import pytest

from app.chunkers.document_chunker import DocumentChunker


def test_split_long_document():
    chunker = DocumentChunker(chunk_size=5, overlap=2)

    chunks = chunker.split("1234567890")

    assert chunks == [
        "12345",
        "45678",
        "7890"
    ]


def test_split_short_document():
    chunker = DocumentChunker(chunk_size=10, overlap=2)

    assert chunker.split("Hello") == ["Hello"]


def test_split_empty_document():
    chunker = DocumentChunker()

    assert chunker.split("") == []


def test_reject_invalid_overlap():
    with pytest.raises(ValueError):
        DocumentChunker(chunk_size=10, overlap=10)
