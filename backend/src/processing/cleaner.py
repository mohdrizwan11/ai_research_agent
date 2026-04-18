"""
processing/cleaner.py
---------------------
Text cleaning utilities. Strips junk from scraped/extracted text
before it reaches the LLM.
"""

import re
import logging

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Remove noise from raw scraped or API text.

    Steps:
        1. Collapse multiple whitespace / newlines
        2. Remove non-printable characters
        3. Strip leading/trailing whitespace
    """
    if not text:
        return ""

    # Remove non-ASCII control characters (keep newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Collapse 3+ blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    # Strip surrounding whitespace
    text = text.strip()

    logger.debug("Cleaned text: %d chars", len(text))
    return text


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    raw = "  Hello\n\n\n\nworld!   Extra   spaces.  "
    print(repr(clean_text(raw)))
