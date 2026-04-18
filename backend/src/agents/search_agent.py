"""
agents/search_agent.py
----------------------
Decides WHICH tools to call and HOW MANY sources to gather.
This is the "planning" agent — it doesn't summarise, it just
collects raw text from multiple sources and returns them.
"""

import logging
import os
import sys

# Allow direct execution: python src/agents/search_agent.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.tools.wiki_tool   import fetch_wikipedia
from src.tools.arxiv_tool  import search_arxiv
from src.tools.search_tool import search_web
from src.tools.scraper_tool import scrape_url
from src.tools.academic_tools import search_openalex, search_semantic_scholar

logger = logging.getLogger(__name__)


def run(topic: str, use_wiki=True, use_arxiv=True,
        use_web=True, deep_research=False) -> list[dict]:
    """
    Gather raw content from all enabled sources.

    Returns a list of source dicts:
        {title, text, url, source_type}
    """
    sources = []

    # ── Wikipedia ──────────────────────────────────────────
    if use_wiki and not deep_research:
        logger.info("[SearchAgent] Querying Wikipedia...")
        wiki = fetch_wikipedia(topic)
        if wiki["extract"]:
            sources.append({
                "title":       wiki["title"],
                "text":        wiki["extract"],
                "url":         wiki["url"],
                "source_type": "wikipedia",
            })

    # ── arXiv ──────────────────────────────────────────────
    if use_arxiv:
        logger.info("[SearchAgent] Querying arXiv...")
        papers = search_arxiv(topic, max_results=3 if deep_research else 2)
        for p in papers:
            if p["summary"]:
                sources.append({
                    "title":       p["title"],
                    "text":        p["summary"],
                    "url":         p["url"],
                    "source_type": "arxiv",
                })

    # ── Semantic Scholar & OpenAlex (Deep Research) ─────────
    if deep_research:
        logger.info("[SearchAgent] Querying Semantic Scholar...")
        ss_papers = search_semantic_scholar(topic, limit=3)
        sources.extend(ss_papers)
        
        logger.info("[SearchAgent] Querying OpenAlex...")
        oa_papers = search_openalex(topic, limit=3)
        sources.extend(oa_papers)

    # ── DuckDuckGo + scraping (fallback) ───────────────────
    if use_web and len(sources) < (4 if deep_research else 2):
        logger.info("[SearchAgent] Querying DuckDuckGo (fallback)...")
        hits = search_web(topic, max_results=3)
        for hit in hits:
            if hit["url"] and hit["snippet"]:
                # Try to scrape for more text; fall back to snippet
                scraped = scrape_url(hit["url"])
                text    = scraped if len(scraped) > 200 else hit["snippet"]
                sources.append({
                    "title":       hit["title"],
                    "text":        text,
                    "url":         hit["url"],
                    "source_type": "web",
                })

    logger.info("[SearchAgent] Collected %d sources for '%s'",
                len(sources), topic)
    return sources


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    results = run("transformer neural network", deep_research=True)
    for s in results:
        print(f"[{s['source_type']}] {s['title']} ({len(s['text'])} chars)")
