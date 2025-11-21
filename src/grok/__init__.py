"""
Grok Integration Module - Trend Research & Fact Validation

This module provides Grok API integration for:
- X (Twitter) trend research
- Fact-checking and validation
- Real-time information gathering
"""

from .grok_utils import ask_grok
from .fact_checker import FactChecker

__all__ = ['ask_grok', 'FactChecker']
