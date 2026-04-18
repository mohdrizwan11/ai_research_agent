"""
core/model_factory.py
---------------------
Returns the correct LLM caller based on a provider string.
Useful when you want to swap backends (Groq / Ollama / OpenAI)
without changing agent code.
"""

import logging
from src.core.llm_client import generate_response as groq_generate

logger = logging.getLogger(__name__)

# Registry maps provider name → callable
_PROVIDERS = {
    "groq": groq_generate,
}


def get_llm(provider: str = "groq"):
    """
    Return a generate_response() function for the given provider.

    Usage:
        llm = get_llm("groq")
        answer = llm("Summarise this text: ...")
    """
    fn = _PROVIDERS.get(provider.lower())
    if fn is None:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Available: {list(_PROVIDERS.keys())}"
        )
    logger.info("Using LLM provider: %s", provider)
    return fn


# ── Unit test ───────────────────────────────────────────────
if __name__ == "__main__":
    llm = get_llm("groq")
    print(llm("What is a neural network?"))
