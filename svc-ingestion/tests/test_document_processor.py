import pytest

from app.processors.document_processor import DocumentProcessor


def test_normalize_document_text():
    processor = DocumentProcessor()

    content = "Los carbohidratos proporcionan energía.\r\n\r\n\r\nLa proteína contribuye al mantenimiento de los músculos. "

    result = processor.process(content)

    assert result == (
        "Los carbohidratos proporcionan energía.\n\n"
        "La proteína contribuye al mantenimiento de los músculos."
    )


def test_reject_non_string_content():
    processor = DocumentProcessor()

    with pytest.raises(TypeError, match="Document content must be a string"):
        processor.process(None)
