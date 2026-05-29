"""Tests for Vietnamese text processing."""

import unicodedata

from app.rag.text_processor import VietnameseTextProcessor


def test_normalize_handles_unicode_normalization() -> None:
    processor = VietnameseTextProcessor()
    text = "Bình gas"

    assert processor.normalize(text) == unicodedata.normalize("NFC", text)


def test_normalize_removes_extra_whitespace() -> None:
    processor = VietnameseTextProcessor()

    assert processor.normalize("  Bình   gas \n Petrolimex  ") == "Bình gas Petrolimex"


def test_segment_vietnamese_sentences() -> None:
    processor = VietnameseTextProcessor()

    sentences = processor.segment_sentences("Gas bị rò rỉ. Hãy khóa van ngay.")

    assert len(sentences) >= 2
    assert sentences[0].startswith("Gas")


def test_chunk_text_respects_sentence_boundaries() -> None:
    processor = VietnameseTextProcessor()
    text = "Câu một rất ngắn. Câu hai cũng ngắn. Câu ba kết thúc."

    chunks = processor.chunk_text(text, chunk_size=35, overlap=0)

    assert len(chunks) > 1
    assert all(chunk.endswith(".") for chunk in chunks)


def test_chunk_text_maintains_overlap() -> None:
    processor = VietnameseTextProcessor()
    text = "Câu một rất ngắn. Câu hai cũng ngắn. Câu ba kết thúc."

    chunks = processor.chunk_text(text, chunk_size=35, overlap=10)

    assert len(chunks) > 1
    assert "Câu hai" in chunks[1]


def test_chunk_text_handles_single_long_sentence() -> None:
    processor = VietnameseTextProcessor()
    sentence = "Một câu rất dài " * 80

    chunks = processor.chunk_text(sentence, chunk_size=100)

    assert chunks == [processor.normalize(sentence)]
