import pytest

from app.loaders.document_loader import DocumentLoader


def test_load_txt():
    loader = DocumentLoader()

    result = loader.load("test_data/nutrition_test.txt")

    assert "carbohidratos proveen energía" in result["content"]
    assert result["metadata"]["source"] == "nutrition_test.txt"
    assert result["metadata"]["file_type"] == "txt"


def test_load_pdf(tmp_path):
    import fitz

    pdf_path = tmp_path / "nutrition_test.pdf"

    # Create a temporary PDF containing sample nutritition test
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72), "La proteína contribuye al mantenimiento muscular")
    document.save(pdf_path)
    document.close()

    loader = DocumentLoader()
    result = loader.load(str(pdf_path))

    assert "La proteína contribuye al mantenimiento muscular" in result["content"]
    assert result["metadata"]["source"] == "nutrition_test.pdf"
    assert result["metadata"]["file_type"] == "pdf"


def test_load_nonexistent_file():
    loader = DocumentLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("test_data/nonexistent.txt")


def test_load_unsopported_extension(tmp_path):
    unsopported_file = tmp_path / "nutrition.docx"
    unsopported_file.write_text("Sample content", encoding="utf-8")

    loader = DocumentLoader()

    with pytest.raises(ValueError, match="unsopported document type"):
        loader.load(str(unsopported_file))
