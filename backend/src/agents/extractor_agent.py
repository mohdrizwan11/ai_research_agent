"""
agents/extractor_agent.py
-------------------------
Takes raw sources from the SearchAgent and applies
cleaning + chunking before passing to the Summarizer.
Keeps each source under a safe token limit.
"""

import logging
import os
import sys

# Allow direct execution: python src/agents/extractor_agent.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.processing.cleaner import clean_text
from src.processing.chunker import chunk_text

logger = logging.getLogger(__name__)

# Keep at most this many characters per source before summarising
_MAX_CHARS = 2000


def run(sources: list[dict]) -> list[dict]:
    """
    Clean and trim each source dict in-place.

    Adds/updates:
        text  : cleaned, truncated text ready for LLM
        chunk : first chunk if text was split

    Returns the same list with cleaned text.
    """
    cleaned = []
    for src in sources:
        raw  = src.get("text", "")
        text = clean_text(raw)

        # Chunk to avoid context overflow
        chunks = chunk_text(text, chunk_size=_MAX_CHARS)
        excerpt = chunks[0] if chunks else ""

        if len(excerpt) < 100:
            logger.debug("[Extractor] Skipping short source: %s", src.get("title"))
            continue

        cleaned.append({**src, "text": excerpt})
        logger.debug("[Extractor] Cleaned '%s': %d chars",
                     src.get("title", "?"), len(excerpt))

    logger.info("[Extractor] %d/%d sources passed cleaning",
                len(cleaned), len(sources))
    return cleaned


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    dummy = [{"title": "Test", "text": "  Hello   world.  " * 200,
              "url": "", "source_type": "test"}]
    out = run(dummy)
    print(out[0]["text"][:100])
