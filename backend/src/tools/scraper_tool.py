"""
tools/scraper_tool.py
---------------------
Fallback web scraper using requests + BeautifulSoup.
Used when APIs don't provide enough text for a given URL.
"""

import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ResearchAgentBot/1.0)"
    )
}


def scrape_url(url: str, max_paragraphs: int = 30) -> str:
    """
    Fetch a webpage and extract clean paragraph text.

    Args:
        url            : Full URL to scrape.
        max_paragraphs : Limit paragraphs to keep size manageable.

    Returns:
        Plain text string, or empty string on failure.
    """
    try:
        response = requests.get(url, headers=_HEADERS, timeout=8)
        response.raise_for_status()

        soup  = BeautifulSoup(response.text, "lxml")

        # Remove noisy tags
        for tag in soup(["script", "style", "nav", "footer",
                          "header", "aside", "form"]):
            tag.decompose()

        paragraphs = [
            p.get_text(separator=" ", strip=True)
            for p in soup.find_all("p")
            if len(p.get_text(strip=True)) > 40   # skip tiny snippets
        ]

        text = " ".join(paragraphs[:max_paragraphs])
        logger.info("Scraped %d chars from %s", len(text), url)
        return text

    except Exception as exc:
        logger.warning("Scraping failed for '%s': %s", url, exc)
        return ""


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    text = scrape_url("https://en.wikipedia.org/wiki/Neural_network")
    print(text[:400])
