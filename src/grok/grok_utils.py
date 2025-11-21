"""
Grok Utils - Grok API utilities for Sisters-On-WhatsApp

Provides core Grok API functionality for:
- X (Twitter) search and trend research
- Fact validation
- Real-time information gathering
"""

import os
import logging
from pathlib import Path
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "grok"
load_dotenv(PROJECT_ROOT / ".env")


def _load_prompt(filename: str) -> str:
    """Load prompt from file, return empty string if not found"""
    prompt_file = PROMPTS_DIR / filename
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        logger.warning(f"⚠️ Prompt file not found: {prompt_file}")
        return ""


def ask_grok(
    question: str,
    x_handles: list = None,
    model: str = None,
    temperature: float = 0.7
) -> str:
    """
    Ask Grok API a question with optional X (Twitter) search

    Args:
        question: Question to ask
        x_handles: Optional list of X handles to search (e.g., ["elonmusk", "OpenAI"])
        model: Optional model name (defaults to env GROK_MODEL)
        temperature: Response temperature (0.0-1.0)

    Returns:
        Grok's response as string, or None if error

    Example:
        >>> response = ask_grok("What are the latest AI trends?")
        >>> response = ask_grok(
        ...     "What's happening with VTubers?",
        ...     x_handles=["hololive", "nijisanji_world"]
        ... )
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        logger.error("❌ XAI_API_KEY not set in environment")
        return None

    url = "https://api.x.ai/v1/chat/completions"

    # Use model from parameter or environment (default: grok-4-fast-reasoning)
    model_name = model or os.getenv("GROK_MODEL", "grok-4-fast-reasoning")

    # Load system prompt from file (Rule #1: NO HARDCODED PROMPTS)
    system_prompt = _load_prompt("search_system_prompt.txt")

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "model": model_name,
        "temperature": temperature,
        "search_parameters": {
            "mode": "on",
            "return_citations": True
        }
    }

    # Filter by specific X handles if provided
    if x_handles:
        payload["search_parameters"]["sources"] = [
            {"type": "x", "x_handles": x_handles}
        ]
        logger.info(f"🔍 X search targeting: {', '.join(x_handles)}")
    else:
        logger.info("🔍 X search: general mode")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        logger.info(f"✅ Grok API call successful (model: {model_name})")
        return answer

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Grok API call failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"❌ Failed to parse Grok API response: {e}")
        return None


def ask_grok_no_search(question: str, model: str = None, temperature: float = 0.7) -> str:
    """
    Ask Grok without X search (for fact-checking, reasoning tasks)

    Args:
        question: Question to ask
        model: Optional model name (defaults to env GROK_MODEL)
        temperature: Response temperature (0.0-1.0)

    Returns:
        Grok's response as string, or None if error
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        logger.error("❌ XAI_API_KEY not set in environment")
        return None

    url = "https://api.x.ai/v1/chat/completions"
    model_name = model or os.getenv("GROK_MODEL", "grok-4-fast-reasoning")

    # Load system prompt from file (Rule #1: NO HARDCODED PROMPTS)
    system_prompt = _load_prompt("fact_check_system_prompt.txt")

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "model": model_name,
        "temperature": temperature
        # No search_parameters - pure reasoning mode
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        logger.info(f"✅ Grok API call successful (no search, model: {model_name})")
        return answer

    except Exception as e:
        logger.error(f"❌ Grok API call failed: {e}")
        return None
