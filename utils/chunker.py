# utils/chunker.py

from __future__ import annotations

from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[str]:
    """
    Split text into overlapping chunks.
    """

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        start += chunk_size - overlap

    return chunks


def chunk_pdf_pages(
    pages_data: List[Dict],
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[Dict]:
    """
    Chunk PDF page text while preserving metadata.
    """

    all_chunks = []

    for page in pages_data:
        text_chunks = chunk_text(
            text=page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for idx, chunk in enumerate(text_chunks):
            all_chunks.append(
                {
                    "content": chunk,
                    "source": page["source"],
                    "page_number": page["page_number"],
                    "chunk_id": f"{page['source']}_page_{page['page_number']}_chunk_{idx}",
                }
            )

    return all_chunks


def chunk_youtube_transcript(
    transcript_data: List[Dict],
    chunk_size: int = 500,
) -> List[Dict]:
    """
    Chunk YouTube transcript while preserving timestamps.
    """

    chunks = []

    current_chunk = []
    current_word_count = 0

    start_timestamp = None

    for entry in transcript_data:
        text = entry["text"]

        words = text.split()

        if start_timestamp is None:
            start_timestamp = entry["timestamp"]

        current_chunk.append(text)

        current_word_count += len(words)

        if current_word_count >= chunk_size:
            chunks.append(
                {
                    "content": " ".join(current_chunk),
                    "timestamp": start_timestamp,
                    "source": entry["source"],
                }
            )

            current_chunk = []
            current_word_count = 0
            start_timestamp = None

    if current_chunk:
        chunks.append(
            {
                "content": " ".join(current_chunk),
                "timestamp": start_timestamp,
                "source": entry["source"],
            }
        )

    return chunks