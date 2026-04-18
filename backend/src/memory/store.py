"""
memory/store.py
---------------
Simple JSON-backed memory store.
Saves past research reports so the same topic is not
re-fetched on every run.
"""

import json
import logging
from pathlib import Path

logger  = logging.getLogger(__name__)
_CACHE = Path(__file__).resolve().parent.parent.parent / "data" / "cache" / "memory.json"


def _load() -> dict:
    if _CACHE.exists():
        try:
            return json.loads(_CACHE.read_text())
        except Exception:
            return {}
    return {}


def _save(data: dict) -> None:
    _CACHE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE.write_text(json.dumps(data, indent=2))


def save(topic: str, report: str, sources: list[dict]) -> None:
    """
    Persist a finished report keyed by topic.
    """
    data         = _load()
    key          = topic.strip().lower()
    data[key]    = {"report": report, "sources": sources}
    _save(data)
    logger.info("[Memory] Saved report for '%s'", topic)


def exists(topic: str) -> bool:
    """Return True if a cached report exists for this topic."""
    return topic.strip().lower() in _load()


def get(topic: str) -> dict | None:
    """
    Retrieve a cached report.

    Returns dict {report, sources} or None if not cached.
    """
    data = _load()
    return data.get(topic.strip().lower())


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    save("test topic", "This is a test report.", [])
    print(exists("test topic"))    # True
    print(exists("other topic"))  # False
    r = get("test topic")
    if r is not None:
        print(r["report"])
