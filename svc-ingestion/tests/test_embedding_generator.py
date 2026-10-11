import pytest
from app.embeddings.embedding_generator import EmbeddingGenerator

@pytest.fixture(scope="module")
def generator():
    return EmbeddingGenerator()

def test_generate_embedding(generator):
    embedding = generator.generate("La avena contine fibra.")

    assert len(embedding) == 384
    assert all(isinstance(value, float) for value in embedding)

def test_generate_batch(generator):
    embeddings = generator.generate_batch([
        "La avena contine fibra.",
        "El huevo aporta proteínas."
    ])

    assert len(embeddings) == 2
    assert all(len(embedding) == 384 for embedding in embeddings)

def test_reject_empty_text(generator):
    with pytest.raises(ValueError):
        generator.generate("")

def test_empty_batch(generator):
    assert generator.generate_batch([]) == []