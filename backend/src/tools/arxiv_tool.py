"""
tools/arxiv_tool.py
-------------------
Search arXiv for academic papers on a topic.
Free, no API key required.
"""

import requests
import feedparser
import logging

logger = logging.getLogger(__name__)
_BASE = "http://export.arxiv.org/api/query"


def search_arxiv(query: str, max_results: int = 3) -> list[dict]:
    """
    Search arXiv and return a list of paper summaries.

    Each item in the list contains:
        title   : paper title
        summary : abstract text
        url     : link to abstract page
        authors : comma-separated author names
    """
    try:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
        }
        response = requests.get(_BASE, params=params, timeout=10)
        response.raise_for_status()

        feed    = feedparser.parse(response.text)
        results = []

        for entry in feed.entries:
            raw_title = entry.get("title", "")
            raw_summary = entry.get("summary", "")
            raw_link = entry.get("link", "")
            raw_authors = entry.get("authors", [])

            title = raw_title.replace("\n", " ").strip() if isinstance(raw_title, str) else ""
            summary = raw_summary.strip() if isinstance(raw_summary, str) else ""
            url = raw_link if isinstance(raw_link, str) else ""

            author_names = []
            if isinstance(raw_authors, list):
                for a in raw_authors:
                    if isinstance(a, dict):
                        name = a.get("name", "")
                        if isinstance(name, str) and name:
                            author_names.append(name)

            results.append({
                "title": title,
                "summary": summary,
                "url": url,
                "authors": ", ".join(author_names),
            })
            logger.debug("arXiv result: %s", results[-1]["title"])

        logger.info("arXiv: found %d results for '%s'", len(results), query)
        return results

    except Exception as exc:
        logger.warning("arXiv search failed for '%s': %s", query, exc)
        return []


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    papers = search_arxiv("large language models", max_results=2)
    for p in papers:
        print(p["title"])
        print(p["url"])
        print()
