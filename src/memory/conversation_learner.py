"""
Conversation learning system - Extract and store corrections from user conversations.

When users correct the sisters (e.g., "Actually, it's called 心斎橋焙煎所"),
this system:
1. Detects corrections in conversation
2. Extracts factual information
3. Stores as pending facts for verification
4. After Grok verification, adds to sisters' memory
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json


class CorrectionDetector:
    """Detect when users are providing corrections or factual information."""

    # Patterns that indicate user is correcting/providing info
    CORRECTION_PATTERNS = [
        # English (specific patterns first)
        r"(?:it'?s|its?)\s+called\s+(.+)",
        r"(?:it'?s|its?)\s+named\s+(.+)",
        r"(?:correct|real|actual)\s+name\s+is\s+(.+)",
        r"actually[,\s]+(?:it'?s|its?)\s+(.+)",
        r"no[,\s]+(?:it'?s|its?)\s+(.+)",

        # Chinese
        r"其實是\s*(.+)",
        r"實際上是\s*(.+)",
        r"正確(?:的)?名字是\s*(.+)",
        r"應該是\s*(.+)",
        r"叫做\s*(.+)",
        r"叫\s*(.+)",
        r"是\s*「(.+?)」",
        r"那家店叫\s*(.+)",
    ]

    # Patterns for extracting place information
    PLACE_PATTERNS = [
        r"(.+?)\s+(?:in|at|on)\s+(.+)",  # "LINK in Shinsaibashi"
        r"(.+?)\s+(?:is a|is an)\s+(.+)",  # "心斎橋焙煎所 is a cafe"
        r"(.+?)[\(（](.+?)[\)）]",  # "心斎橋焙煎所 (Shinsaibashi)"
    ]

    def detect_correction(self, message: str) -> Optional[Dict]:
        """
        Detect if message contains a correction or factual information.

        Args:
            message: User's message

        Returns:
            {
                "type": "correction",
                "original_text": "Actually, it's called 心斎橋焙煎所",
                "extracted_fact": "心斎橋焙煎所",
                "confidence": 0.8,
                "category": "place"
            }
            or None if no correction detected
        """
        message_lower = message.lower()

        # Check for correction patterns
        for pattern in self.CORRECTION_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()

                # Clean up extracted text
                extracted = self._clean_extracted_text(extracted)

                if extracted:
                    return {
                        "type": "correction",
                        "original_text": message,
                        "extracted_fact": extracted,
                        "confidence": 0.8,
                        "category": self._categorize_fact(extracted)
                    }

        # Check if message contains business names (quoted or specific format)
        if self._looks_like_business_name(message):
            extracted = self._extract_business_name(message)
            if extracted:
                return {
                    "type": "information",
                    "original_text": message,
                    "extracted_fact": extracted,
                    "confidence": 0.6,
                    "category": "place"
                }

        return None

    def _clean_extracted_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove trailing punctuation
        text = re.sub(r'[,.!?;:。，！？；：]+$', '', text)

        # Remove quotes
        text = text.strip('"\'「」『』""''')

        return text.strip()

    def _categorize_fact(self, text: str) -> str:
        """Categorize the type of fact."""
        text_lower = text.lower()

        # Check for place indicators
        place_keywords = ['cafe', 'restaurant', 'shop', 'store', 'bar', 'hotel',
                         'カフェ', '店', 'レストラン', '焙煎所', '専門店']
        if any(kw in text_lower for kw in place_keywords):
            return "place"

        # Check for book/media indicators
        media_keywords = ['book', 'novel', 'manga', 'anime', 'film', 'movie']
        if any(kw in text_lower for kw in media_keywords):
            return "media"

        # Check for person indicators
        person_keywords = ['sensei', 'master', 'teacher', 'professor', '先生', '師匠']
        if any(kw in text_lower for kw in person_keywords):
            return "person"

        return "general"

    def _looks_like_business_name(self, text: str) -> bool:
        """Check if text looks like it contains a business name."""
        # Check for quotes around text (common when mentioning names)
        if re.search(r'[「」『』""'']', text):
            return True

        # Check for capital words (English names)
        if re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text):
            return True

        # Check for Japanese business patterns
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]{2,}(?:店|カフェ|焙煎所|専門店)', text):
            return True

        return False

    def _extract_business_name(self, text: str) -> Optional[str]:
        """Extract business name from text."""
        # Try quoted text first
        quoted = re.search(r'[「『"\'](.+?)[」』"\']', text)
        if quoted:
            return quoted.group(1).strip()

        # Try Japanese business pattern
        japanese = re.search(r'([\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{2,}(?:店|カフェ|焙煎所|専門店|Bar|BAR))', text)
        if japanese:
            return japanese.group(1).strip()

        # Try capitalized English name pattern
        english = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s+(?:Cafe|Coffee|Restaurant|Shop|Bar))?)\b', text)
        if english:
            return english.group(1).strip()

        return None


class ConversationLearner:
    """Learn from conversations and build sisters' memory."""

    def __init__(self, pending_facts_file: Optional[Path] = None):
        if pending_facts_file is None:
            project_root = Path(__file__).parent.parent.parent
            pending_facts_file = project_root / "prompts" / "pending_facts.json"

        self.pending_facts_file = pending_facts_file
        self.detector = CorrectionDetector()
        self.pending_facts = self._load_pending_facts()

    def _load_pending_facts(self) -> Dict:
        """Load pending facts awaiting verification."""
        if self.pending_facts_file.exists():
            with open(self.pending_facts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "pending": [],
                "verified": [],
                "rejected": [],
                "last_updated": None
            }

    def _save_pending_facts(self) -> None:
        """Save pending facts to file."""
        self.pending_facts_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.pending_facts_file, 'w', encoding='utf-8') as f:
            json.dump(self.pending_facts, f, ensure_ascii=False, indent=2)

    def process_message(self, user_message: str, phone_number: str,
                       conversation_context: Optional[str] = None) -> Optional[Dict]:
        """
        Process a user message to detect corrections/facts.

        Args:
            user_message: User's message
            phone_number: User's phone number
            conversation_context: Recent conversation history (optional)

        Returns:
            Detection result or None
        """
        result = self.detector.detect_correction(user_message)

        if result:
            # Add to pending facts
            fact_entry = {
                "fact": result["extracted_fact"],
                "category": result["category"],
                "confidence": result["confidence"],
                "source": {
                    "phone_number": phone_number,
                    "message": user_message,
                    "context": conversation_context[:500] if conversation_context else None,
                    "timestamp": datetime.now().isoformat()
                },
                "status": "pending",
                "verification": None
            }

            # Check if similar fact already exists
            if not self._is_duplicate(fact_entry):
                self.pending_facts["pending"].append(fact_entry)
                self.pending_facts["last_updated"] = datetime.now().isoformat()
                self._save_pending_facts()

                print(f"✅ Detected user correction: {result['extracted_fact']}")
                return result

        return None

    def _is_duplicate(self, new_fact: Dict) -> bool:
        """Check if fact is duplicate of existing pending fact."""
        new_text = new_fact["fact"].lower()

        for existing in self.pending_facts["pending"]:
            if existing["fact"].lower() == new_text:
                return True

        return False

    def get_pending_facts(self, category: Optional[str] = None,
                         min_confidence: float = 0.5) -> List[Dict]:
        """Get pending facts for verification."""
        pending = self.pending_facts.get("pending", [])

        # Filter by category if specified
        if category:
            pending = [f for f in pending if f["category"] == category]

        # Filter by confidence
        pending = [f for f in pending if f["confidence"] >= min_confidence]

        return pending

    def mark_verified(self, fact: str, verification_data: Dict) -> None:
        """Mark a pending fact as verified."""
        for i, pending_fact in enumerate(self.pending_facts["pending"]):
            if pending_fact["fact"] == fact:
                pending_fact["status"] = "verified"
                pending_fact["verification"] = verification_data
                pending_fact["verified_at"] = datetime.now().isoformat()

                # Move to verified list
                self.pending_facts["verified"].append(pending_fact)
                self.pending_facts["pending"].pop(i)

                self._save_pending_facts()
                print(f"✅ Marked as verified: {fact}")
                break

    def mark_rejected(self, fact: str, reason: str) -> None:
        """Mark a pending fact as rejected."""
        for i, pending_fact in enumerate(self.pending_facts["pending"]):
            if pending_fact["fact"] == fact:
                pending_fact["status"] = "rejected"
                pending_fact["rejection_reason"] = reason
                pending_fact["rejected_at"] = datetime.now().isoformat()

                # Move to rejected list
                self.pending_facts["rejected"].append(pending_fact)
                self.pending_facts["pending"].pop(i)

                self._save_pending_facts()
                print(f"❌ Marked as rejected: {fact} (reason: {reason})")
                break

    def get_stats(self) -> Dict:
        """Get statistics about learned facts."""
        return {
            "pending": len(self.pending_facts.get("pending", [])),
            "verified": len(self.pending_facts.get("verified", [])),
            "rejected": len(self.pending_facts.get("rejected", [])),
            "last_updated": self.pending_facts.get("last_updated")
        }
