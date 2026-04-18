"""
agents/summarizer_agent.py
--------------------------
Summarises each cleaned source individually using the LLM.
Returns bullet-point summaries per source.
"""

import logging
import os
import sys
from pathlib import Path

# Allow direct execution: python src/agents/summarizer_agent.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.llm_client import generate_response

logger = logging.getLogger(__name__)

# Load prompt template once
_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "summarize_prompt.txt"
_PROMPT_TEMPLATE = (
    _PROMPT_PATH.read_text() if _PROMPT_PATH.exists()
    else "Summarise the following text in 5 clear bullet points:\n\n{text}"
)


def summarise_source(source: dict) -> dict:
    """
    Summarise a single source dict.
    Adds a 'summary' key and returns the updated dict.
    """
    text = source.get("text", "")
    if not text:
        return {**source, "summary": ""}

    prompt = _PROMPT_TEMPLATE.format(text=text)
    summary = generate_response(
        prompt,
        system="You are a precise academic summariser. Be concise and factual.",
    )
    logger.info("[Summarizer] Summarised '%s'", source.get("title", "?"))
    return {**source, "summary": summary}


def run(sources: list[dict]) -> list[dict]:
    """
    Summarise all sources. Returns updated list with 'summary' added.
    """
    results = [summarise_source(s) for s in sources]
    logger.info("[Summarizer] Summarised %d sources", len(results))
    return results


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    test = [{"title": "AI Basics",
             "text":  "Artificial intelligence is the simulation of human "
                      "intelligence in machines programmed to think and learn.",
             "url": "", "source_type": "test"}]
    out = run(test)
    print(out[0]["summary"])
