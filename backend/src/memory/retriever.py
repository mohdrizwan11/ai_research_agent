"""
memory/retriever.py
-------------------
Retrieves and displays cached research from the store.
"""

import logging
from src.memory.store import get, exists

logger = logging.getLogger(__name__)


def retrieve(topic: str) -> str | None:
    """
    Return a previously saved report for *topic*, or None.

    Usage:
        cached = retrieve("quantum computing")
        if cached:
            print(cached)
    """
    if not exists(topic):
        logger.info("[Retriever] No cache for '%s'", topic)
        return None

    entry = get(topic)
    logger.info("[Retriever] Cache hit for '%s'", topic)
    return entry["report"] if entry else None


def list_cached_topics() -> list[str]:
    """Return a list of all topics that have been cached."""
    from src.memory.store import _load
    return list(_load().keys())


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    print(list_cached_topics())
