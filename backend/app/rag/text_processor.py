"""Vietnamese text processing utilities for RAG."""

import re
import unicodedata

from app.core.logging import get_logger


class VietnameseTextProcessor:
    """Normalize, segment, and chunk Vietnamese text for retrieval."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def normalize(self, text: str) -> str:
        """Normalize Vietnamese text and collapse whitespace."""
        if not text:
            return ""
        normalized = unicodedata.normalize("NFC", text)
        normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')
        normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")
        normalized = normalized.replace("\u2013", "-").replace("\u2014", "-")
        return " ".join(normalized.split())

    def segment_sentences(self, text: str) -> list[str]:
        """Split Vietnamese text into sentences."""
        normalized = self.normalize(text)
        if not normalized:
            return []
        try:
            from underthesea import sent_tokenize

            sentences = sent_tokenize(normalized)
        except (ImportError, RuntimeError):
            sentences = re.split(r"(?<=[.!?])\s+", normalized)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Chunk text at sentence boundaries with sentence overlap."""
        normalized = self.normalize(text)
        if not normalized:
            return []
        if len(normalized) <= chunk_size:
            return [normalized]

        sentences = self.segment_sentences(normalized)
        chunks: list[str] = []
        current: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if sentence_length > chunk_size:
                if current:
                    chunks.append(" ".join(current))
                    current = []
                    current_length = 0
                chunks.append(sentence)
                continue

            if current and current_length + sentence_length + 1 > chunk_size:
                chunks.append(" ".join(current))
                if overlap > 0:
                    overlap_sentences: list[str] = []
                    overlap_length = 0
                    for existing in reversed(current):
                        overlap_sentences.insert(0, existing)
                        overlap_length += len(existing) + 1
                        if overlap_length >= overlap:
                            break
                    current = [*overlap_sentences, sentence]
                    current_length = sum(len(item) + 1 for item in current)
                else:
                    current = [sentence]
                    current_length = sentence_length + 1
            else:
                current.append(sentence)
                current_length += sentence_length + 1

        if current:
            chunks.append(" ".join(current))
        return chunks
