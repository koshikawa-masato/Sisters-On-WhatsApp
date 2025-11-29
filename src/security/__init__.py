"""Security module for input validation and injection protection."""

from .prompt_injection import PromptInjectionDetector

__all__ = ["PromptInjectionDetector"]
