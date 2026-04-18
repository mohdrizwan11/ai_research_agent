"""
tools/wiki_tool.py
------------------
Fetch a clean plain-text summary from Wikipedia.
No API key needed — completely free.
"""

import requests
import logging

logger = logging.getLogger(__name__)
_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"
_ALT_BASE = "https://en.wikipedia.org/w/api.php"
_HEADERS = {
    "User-Agent": "ai-research-agent/1.0 (educational-use; +https://example.local)",
    "Accept": "application/json",
}


def fetch_wikipedia(topic: str) -> dict:
    """
    Fetch a Wikipedia summary for *topic*.

    Returns a dict with keys:
        title   : article title
        extract : plain-text summary paragraph(s)
        url     : link to full article
    """
    try:
        # Replace spaces with underscores for the URL
        slug = topic.strip().replace(" ", "_")
        response = requests.get(f"{_BASE}/{slug}", headers=_HEADERS, timeout=8)

        if response.status_code == 403:
            # Fallback for environments where REST summary endpoint is blocked.
            alt_params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": 1,
                "explaintext": 1,
                "inprop": "url",
                "titles": topic,
                "format": "json",
                "redirects": 1,
            }
            alt_resp = requests.get(_ALT_BASE, params=alt_params, headers=_HEADERS, timeout=8)
            alt_resp.raise_for_status()
            alt_data = alt_resp.json().get("query", {}).get("pages", {})
            page = next(iter(alt_data.values()), {}) if isinstance(alt_data, dict) else {}

            result = {
                "title": page.get("title", topic),
                "extract": page.get("extract", ""),
                "url": page.get("fullurl", ""),
            }
            logger.info("Wikipedia fallback: fetched '%s' (%d chars)",
                        result["title"], len(result["extract"]))
            return result

        response.raise_for_status()
        data = response.json()

        result = {
            "title":   data.get("title", topic),
            "extract": data.get("extract", ""),
            "url":     data.get("content_urls", {})
                           .get("desktop", {})
                           .get("page", ""),
        }
        logger.info("Wikipedia: fetched '%s' (%d chars)",
                    result["title"], len(result["extract"]))
        return result

    except Exception as exc:
        logger.warning("Wikipedia fetch failed for '%s': %s", topic, exc)
        return {"title": topic, "extract": "", "url": ""}


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    r = fetch_wikipedia("Artificial Intelligence")
    print(r["title"])
    print(r["extract"][:300])
    print(r["url"])
