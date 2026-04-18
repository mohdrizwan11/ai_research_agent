"""
tools/search_tool.py
--------------------
Web search using DuckDuckGo — completely free, no API key.
Returns a list of {title, url, snippet} dicts.
"""

import requests
import logging

logger = logging.getLogger(__name__)
_BASE = "https://api.duckduckgo.com/"


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web via DuckDuckGo Instant Answer API.

    Note: DuckDuckGo's free API returns instant-answer results
    (RelatedTopics), not full Google-style listings. Works well
    for factual topics; use arXiv/Wikipedia for depth.

    Returns list of dicts: {title, url, snippet}
    """
    try:
        params = {
            "q":      query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
        }
        response = requests.get(_BASE, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

        results = []

        # Abstract (top result)
        if data.get("AbstractURL"):
            results.append({
                "title":   data.get("Heading", query),
                "url":     data["AbstractURL"],
                "snippet": data.get("AbstractText", ""),
            })

        # Related topics
        for item in data.get("RelatedTopics", []):
            if len(results) >= max_results:
                break
            if "FirstURL" in item:
                results.append({
                    "title":   item.get("Text", "")[:80],
                    "url":     item["FirstURL"],
                    "snippet": item.get("Text", ""),
                })

        logger.info("DuckDuckGo: %d results for '%s'", len(results), query)
        return results

    except Exception as exc:
        logger.warning("Web search failed for '%s': %s", query, exc)
        return []


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    hits = search_web("quantum computing basics")
    for h in hits:
        print(h["title"], "->", h["url"])
