"""
processing/chunker.py
---------------------
Splits long text into chunks that fit within the LLM context window.
Uses sentence boundaries when possible to avoid mid-sentence cuts.
"""

import re
import logging

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 2000,
               overlap: int = 100) -> list[str]:
    """
    Split text into overlapping chunks of ~chunk_size characters.

    Args:
        text       : Input string.
        chunk_size : Target max characters per chunk.
        overlap    : Characters of context shared between chunks.

    Returns:
        List of chunk strings.
    """
    if not text:
        return []

    # Split at sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            # New chunk starts with overlap from previous
            current = (current[-overlap:] + " " + sentence).strip()

    if current:
        chunks.append(current)

    logger.debug("Chunked text into %d chunks", len(chunks))
    return chunks


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    sample = "This is sentence one. And this is sentence two. " * 100
    parts  = chunk_text(sample, chunk_size=200)
    print(f"{len(parts)} chunks, first: {parts[0][:60]}...")
