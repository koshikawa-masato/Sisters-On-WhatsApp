"""
Fact Checker - Layer 6 of 7-Layer Defense System

Uses Grok API to verify factual accuracy of user statements
Prevents misinformation propagation in conversation memory
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional
from .grok_utils import ask_grok_no_search

logger = logging.getLogger(__name__)

# Prompts directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "grok"


def _load_prompt_template(filename: str) -> str:
    """Load prompt template from file, return empty string if not found"""
    prompt_file = PROMPTS_DIR / filename
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        logger.warning(f"⚠️ Prompt template not found: {prompt_file}")
        return ""


class FactChecker:
    """
    Fact-checking system using Grok API (Layer 6)

    Validates user statements to prevent misinformation from
    being stored in conversation memory or learned knowledge.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize FactChecker

        Args:
            enabled: Whether fact-checking is enabled (default: True)
        """
        self.enabled = enabled
        if self.enabled:
            logger.info("✅ FactChecker initialized (Grok API enabled)")
        else:
            logger.warning("⚠️ FactChecker initialized (disabled)")

    async def check(self, statement: str) -> Dict:
        """
        Fact-check a user statement

        Args:
            statement: Statement to verify

        Returns:
            {
                'passed': True/False,
                'confidence': 0.0-1.0,
                'verification': 'Grok verification result',
                'correct_info': 'Correct information (if wrong)'
            }
        """
        if not self.enabled:
            logger.debug("⚠️ Fact-checking disabled, skipping")
            return {
                'passed': True,
                'confidence': 0.5,
                'verification': 'Fact-checking disabled'
            }

        try:
            # Load fact-check query template from file (Rule #1: NO HARDCODED PROMPTS)
            fact_check_template = _load_prompt_template("fact_check_query_template.txt")
            fact_check_query = fact_check_template.format(statement=statement)

            # Call Grok API (without X search, pure reasoning)
            grok_result = ask_grok_no_search(question=fact_check_query)

            if not grok_result:
                logger.error("❌ Grok API call failed")
                return {
                    'passed': False,
                    'confidence': 0.5,
                    'verification': 'Grok API call failed'
                }

            # Parse result
            if "CORRECT" in grok_result.upper() and "INCORRECT" not in grok_result.upper():
                logger.info(f"✅ Fact-check passed: {statement[:50]}...")
                return {
                    'passed': True,
                    'confidence': 0.9,
                    'verification': grok_result
                }

            elif "INCORRECT" in grok_result.upper():
                # Extract correct information
                correct_info = self._extract_correct_info(grok_result)
                logger.warning(f"❌ Fact-check failed: {statement[:50]}...")
                logger.info(f"   Correct info: {correct_info}")
                return {
                    'passed': False,
                    'confidence': 0.0,
                    'correct_info': correct_info,
                    'verification': grok_result
                }

            else:
                # Unknown/uncertain
                logger.info(f"⚠️ Fact-check uncertain: {statement[:50]}...")
                return {
                    'passed': False,
                    'confidence': 0.5,
                    'verification': grok_result
                }

        except Exception as e:
            logger.error(f"❌ Fact-check error: {e}")
            return {
                'passed': False,
                'confidence': 0.5,
                'verification': f'Error: {str(e)}'
            }

    def _extract_correct_info(self, grok_result: str) -> str:
        """
        Extract correct information from Grok's response

        Args:
            grok_result: Grok API response

        Returns:
            Correct information string
        """
        # Look for pattern "INCORRECT: the correct information is ..."
        match = re.search(
            r'INCORRECT[:\s]*(?:the\s+)?correct(?:\s+information)?(?:\s+is)?[:\s]+(.+)',
            grok_result,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

        # If pattern doesn't match, return full result
        return grok_result

    def is_serious_topic(self, message: str) -> bool:
        """
        Check if message is about a serious topic requiring strict validation

        Serious topics include: health, finance, legal, safety

        Args:
            message: User message

        Returns:
            True if serious topic detected
        """
        SERIOUS_TOPICS = [
            # Health & Medical
            "health", "medical", "disease", "medicine", "treatment", "symptom",
            "hospital", "doctor", "surgery", "cancer", "diagnosis",
            "vaccine", "prescription", "therapy",

            # Finance
            "money", "investment", "debt", "loan", "stock", "crypto",
            "credit", "mortgage", "bankruptcy", "fraud", "scam",
            "bitcoin", "trading", "portfolio",

            # Legal
            "law", "legal", "crime", "police", "court", "lawyer",
            "illegal", "arrest", "lawsuit", "regulation", "copyright",

            # Safety
            "disaster", "earthquake", "fire", "flood", "emergency",
            "accident", "injury", "danger", "warning", "evacuation"
        ]

        message_lower = message.lower()
        for topic in SERIOUS_TOPICS:
            if topic in message_lower:
                logger.info(f"🚨 Serious topic detected: {topic}")
                return True

        return False

    async def check_contradiction_with_memory(
        self,
        new_info: str,
        character: str,
        existing_memories: list
    ) -> Dict:
        """
        Check if new information contradicts existing verified memories

        Args:
            new_info: New information to check
            character: Character name (Botan, Kasho, Yuri)
            existing_memories: List of existing verified memories

        Returns:
            {
                'contradicts': True/False,
                'existing_memory': {...},  # Contradicting memory
                'reason': 'Contradiction reason'
            }
        """
        if not existing_memories or not self.enabled:
            return {'contradicts': False}

        try:
            # Get most relevant memory (highest similarity)
            most_relevant = max(existing_memories, key=lambda x: x.get('similarity', 0))

            # Load contradiction check template from file (Rule #1: NO HARDCODED PROMPTS)
            contradiction_template = _load_prompt_template("contradiction_check_template.txt")
            contradiction_check_prompt = contradiction_template.format(
                existing_knowledge=most_relevant.get('content', most_relevant.get('meaning', '')),
                new_info=new_info
            )

            grok_result = ask_grok_no_search(question=contradiction_check_prompt)

            if not grok_result:
                logger.error("❌ Grok API call failed (contradiction check)")
                return {'contradicts': False}

            if "CONTRADICTION" in grok_result.upper() and "NO CONTRADICTION" not in grok_result.upper():
                logger.warning(f"⚠️ Contradiction detected: {new_info[:50]}...")
                return {
                    'contradicts': True,
                    'existing_memory': most_relevant,
                    'reason': grok_result
                }

            logger.info(f"✅ No contradiction: {new_info[:50]}...")
            return {'contradicts': False}

        except Exception as e:
            logger.error(f"❌ Contradiction check error: {e}")
            return {'contradicts': False}


# Test code
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test_fact_checker():
        """Test FactChecker functionality"""

        checker = FactChecker()

        # Test 1: Correct information
        print("\n=== Test 1: Correct information ===")
        result = await checker.check("The capital of France is Paris")
        print(f"Result: {result}")

        # Test 2: Incorrect information
        print("\n=== Test 2: Incorrect information ===")
        result = await checker.check("The capital of France is London")
        print(f"Result: {result}")

        # Test 3: Serious topic detection
        print("\n=== Test 3: Serious topic detection ===")
        test_messages = [
            "How do I treat a cold?",
            "I love this ramen!",
            "Should I invest in cryptocurrency?"
        ]

        for msg in test_messages:
            is_serious = checker.is_serious_topic(msg)
            print(f"{msg}: {'SERIOUS' if is_serious else 'NORMAL'}")

    # Run tests
    asyncio.run(test_fact_checker())
