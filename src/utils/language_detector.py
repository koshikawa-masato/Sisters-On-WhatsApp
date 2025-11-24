"""Language detection utility for bilingual support."""

import re


def detect_language(text: str) -> str:
    """
    Detect language of input text (English or Chinese).

    Args:
        text: User's message

    Returns:
        'zh' for Chinese (Simplified/Traditional)
        'en' for English
    """
    # Remove whitespace and punctuation for analysis
    clean_text = re.sub(r'[^\w]', '', text)

    if not clean_text:
        return 'en'  # Default to English for empty text

    # Count Chinese characters (CJK Unified Ideographs)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))

    # If more than 30% Chinese characters, classify as Chinese
    if chinese_chars / len(clean_text) > 0.3:
        return 'zh'
    else:
        return 'en'


def get_language_instruction(language: str) -> str:
    """
    Get instruction for LLM to respond in detected language.

    Args:
        language: 'en' or 'zh'

    Returns:
        Instruction string for system prompt
    """
    if language == 'zh':
        return "\n\nIMPORTANT: The user is speaking Chinese. You MUST respond in Chinese (Traditional or Simplified, match the user's style)."
    else:
        return "\n\nIMPORTANT: The user is speaking English. You MUST respond in English."
