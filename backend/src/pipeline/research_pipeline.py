"""
pipeline/research_pipeline.py
------------------------------
ORCHESTRATOR — wires every agent together into one call.

Flow:
    topic
      └─► search_agent   (fetch raw sources)
      └─► extractor_agent (clean + chunk)
      └─► summarizer_agent (per-source LLM summaries)
      └─► report_agent   (final structured report)
      └─► memory store   (cache for future runs)
"""

import logging
from src.agents   import search_agent, extractor_agent
from src.agents   import summarizer_agent, report_agent
from src.memory   import store, retriever

logger = logging.getLogger(__name__)


def run(topic: str, force_refresh: bool = False, mode: str = "concise", deep_research: bool = False) -> dict:
    """
    Run the full research pipeline for *topic*.

    Args:
        topic         : Research subject.
        force_refresh : Skip cache and re-fetch even if cached.
        mode          : 'short', 'concise', or 'lengthy'.
        deep_research : Toggle for deep research.

    Returns:
        {
          "topic"  : str,
          "report" : str,
          "sources": list[dict],
          "cached" : bool,
        }
    """
    logger.info("=== Pipeline START: '%s' (mode=%s, deep=%s) ===", topic, mode, deep_research)

    # ── 1. Check cache ──────────────────────────────────────
    if not force_refresh and not deep_research: # Do not use cache for deep research directly
        cached = retriever.retrieve(topic)
        if cached:
            logger.info("Returning cached report for '%s'", topic)
            return {"topic": topic, "report": cached,
                    "sources": [], "cached": True}

    # ── 2. Search ───────────────────────────────────────────
    print(f"🔍  Searching sources (Deep: {deep_research})...")
    raw_sources = search_agent.run(topic, deep_research=deep_research)

    if not raw_sources:
        return {"topic": topic,
                "report": "No sources found. Try a more specific topic.",
                "sources": [], "cached": False}

    # ── 3. Extract / clean ──────────────────────────────────
    print("🧹  Cleaning content...")
    clean_sources = extractor_agent.run(raw_sources)

    # ── 4. Summarise ────────────────────────────────────────
    print("🧠  Summarising sources...")
    summarised = summarizer_agent.run(clean_sources)

    # ── 5. Generate report ──────────────────────────────────
    print(f"📄  Generating {mode} report...")
    report = report_agent.run(topic, summarised, mode=mode, deep_research=deep_research)

    # ── 6. Save to memory ───────────────────────────────────
    if not deep_research: # Cache regular reports
        store.save(topic, report, summarised)

    logger.info("=== Pipeline DONE: '%s' ===", topic)
    return {
        "topic":   topic,
        "report":  report,
        "sources": summarised,
        "cached":  False,
        "mode":    mode,
        "deep_research": deep_research
    }
