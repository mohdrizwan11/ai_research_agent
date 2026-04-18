"""
core/llm_client.py
------------------
Single point of contact for all Groq LLM calls.
Every other module imports generate_response() from here.
"""

import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Initialise Groq client once at module level
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_model  = os.getenv("GROQ_MODEL", "llama3-70b-8192")


def generate_response(
    prompt: str,
    system: str = "You are a helpful research assistant.",
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str:
    """
    Send a prompt to Groq and return the text response.

    Args:
        prompt      : The user message / task description.
        system      : System-level instruction for the model.
        max_tokens  : Upper limit on response length.
        temperature : 0 = deterministic, 1 = creative.

    Returns:
        Model reply as plain string, or an error message.
    """
    try:
        logger.debug("Sending prompt to Groq (model=%s)", _model)
        response = _client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        text = content.strip() if content is not None else ""
        logger.debug("Groq responded (%d chars)", len(text))
        return text

    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        return f"[LLM Error]: {exc}"


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    print(generate_response("Explain machine learning in 2 sentences."))
