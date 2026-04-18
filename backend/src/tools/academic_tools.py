"""
tools/academic_tools.py
-----------------------
Free academic tools to augment deep research (OpenAlex and Semantic Scholar).
These APIs do not require API keys for basic usage.
"""

import requests
import logging

logger = logging.getLogger(__name__)

def search_openalex(topic: str, limit: int = 3) -> list[dict]:
    """
    Search OpenAlex API for open access academic works related to the topic.
    Returns a list of clean source dicts.
    """
    logger.info("[OpenAlex] Searching for '%s'", topic)
    results = []
    try:
        url = "https://api.openalex.org/works"
        params = {
            "search": topic,
            "per-page": limit,
            "filter": "is_oa:true,has_abstract:true",
            "sort": "relevance_score:desc"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        for work in data.get("results", []):
            abstract = _build_abstract(work.get("abstract_inverted_index", {}))
            if abstract:
                results.append({
                    "title": work.get("title", ""),
                    "url": work.get("id", ""),
                    "text": abstract,
                    "source_type": "openalex"
                })
    except Exception as e:
        logger.warning("[OpenAlex] Search failed: %s", e)
        
    return results

def search_semantic_scholar(topic: str, limit: int = 3) -> list[dict]:
    """
    Search Semantic Scholar API for academic papers.
    Returns a list of clean source dicts.
    """
    logger.info("[SemanticScholar] Searching for '%s'", topic)
    results = []
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": topic,
            "limit": limit,
            "fields": "title,url,abstract"
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        for paper in data.get("data", []):
            if paper.get("abstract"):
                results.append({
                    "title": paper.get("title", ""),
                    "url": paper.get("url", ""),
                    "text": paper.get("abstract", ""),
                    "source_type": "semanticscholar"
                })
    except Exception as e:
        logger.warning("[SemanticScholar] Search failed: %s", e)
        
    return results

def _build_abstract(inverted_index: dict) -> str:
    """Rebuild abstract string from OpenAlex inverted index"""
    if not inverted_index:
        return ""
    
    # inverted_index format: {"word": [pos1, pos2]}
    word_index = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_index.append((pos, word))
            
    word_index.sort(key=lambda x: x[0])
    return " ".join([word for _, word in word_index])

if __name__ == "__main__":
    print(search_openalex("deep learning"))
    print(search_semantic_scholar("deep learning"))
