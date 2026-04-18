"""
agents/report_agent.py
----------------------
Combines all per-source summaries into a single structured
research report with Introduction, Key Findings, Insights,
and Conclusion sections.
"""

import logging
import os
import sys
from pathlib import Path

# Allow direct execution: python src/agents/report_agent.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.llm_client import generate_response

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "report_prompt.txt"
_PROMPT_TEMPLATE = (
    _PROMPT_PATH.read_text() if _PROMPT_PATH.exists()
    else (
        "Write a structured research report on: {topic}\n\n"
        "Include:\n"
        "- Introduction\n"
        "- Key Findings\n"
        "- Insights\n"
        "- Conclusion\n"
        "- References\n\n"
        "Use this summarised content:\n{summaries}"
    )
)


def run(topic: str, sources: list[dict], mode: str = "concise", deep_research: bool = False) -> str:
    """
    Generate the final research report.

    Args:
        topic   : Research topic string.
        sources : List of source dicts (must have 'summary', 'title', 'url').
        mode    : 'short', 'concise', or 'lengthy'
        deep_research : Toggle for deep research.

    Returns:
        Formatted report as a plain string.
    """
    # Build a numbered list of summaries with citations
    numbered = []
    for i, src in enumerate(sources, 1):
        summary = src.get("summary", "").strip()
        title   = src.get("title", f"Source {i}")
        url     = src.get("url", "")
        if summary:
            numbered.append(
                f"[{i}] {title}\n{summary}\nSource: {url}"
            )

    if not numbered:
        return "No source content available to generate a report."

    combined = "\n\n".join(numbered)
    
    sys_prompt = "You are an expert research writer. Write clearly, cite sources by number."
    
    if mode == "short":
        sys_prompt += "\nWrite a SHORT research overview: exactly 150-200 words. No markdown headers. Two or three dense paragraphs. Pure facts, no padding."
        max_tokens = 500
        prompt = f"Topic: {topic}\n\nSummarised Content:\n{combined}"
    elif mode == "lengthy":
        sys_prompt += "\nWrite a COMPREHENSIVE report (800-1000 words) in markdown with ALL sections: Introduction, Background, Key Findings, Critical Analysis, Implications, Conclusion."
        max_tokens = 2500
        prompt = f"Write a comprehensive report on: {topic}\n\nSummarised Content:\n{combined}"
    else: # concise
        sys_prompt += "\nWrite a CONCISE structured report (400-600 words) in markdown with sections: Overview, Key Findings (bulleted), Conclusion."
        max_tokens = 1500
        prompt = f"Write a concise report on: {topic}\n\nSummarised Content:\n{combined}"

    if deep_research:
        sys_prompt += "\nDEEP RESEARCH MODE: Begin your response with exactly one line: 'ANGLES: angle1, angle2, angle3, angle4' — four specific sub-angles to explore. Then write the full report."
        max_tokens += 1000

    logger.info("[ReportAgent] Generating %s report for '%s' (Deep: %s)", mode, topic, deep_research)
    report = generate_response(
        prompt,
        system=sys_prompt,
        max_tokens=max_tokens,
    )
    return report


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    dummy = [{
        "title":   "Deep Learning Overview",
        "summary": "• Neural networks learn from data\n• Widely used in vision and NLP",
        "url":     "https://example.com",
    }]
    print(run("Deep Learning", dummy))
