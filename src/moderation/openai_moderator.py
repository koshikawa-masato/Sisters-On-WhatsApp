"""OpenAI Moderation API integration (Layer 2)."""

import os
from typing import Dict, Optional
from openai import AsyncOpenAI


class ModerationResult:
    """Result from content moderation."""

    def __init__(
        self,
        is_flagged: bool,
        categories: Dict[str, bool],
        category_scores: Dict[str, float],
        blocked_reason: Optional[str] = None
    ):
        self.is_flagged = is_flagged
        self.categories = categories
        self.category_scores = category_scores
        self.blocked_reason = blocked_reason

    def should_block(self) -> bool:
        """Determine if content should be blocked."""
        return self.is_flagged

    def get_primary_violation(self) -> Optional[str]:
        """Get the primary violation category."""
        if not self.is_flagged:
            return None

        # Find the category with highest score
        flagged_categories = {
            cat: score
            for cat, score in self.category_scores.items()
            if self.categories.get(cat, False)
        }

        if not flagged_categories:
            return None

        return max(flagged_categories.items(), key=lambda x: x[1])[0]


class OpenAIModerator:
    """OpenAI Moderation API wrapper."""

    # Critical categories that always block
    CRITICAL_CATEGORIES = [
        "sexual/minors",
        "hate/threatening",
        "violence/graphic",
        "self-harm/intent"
    ]

    # High-risk categories (configurable threshold)
    HIGH_RISK_CATEGORIES = [
        "sexual",
        "hate",
        "violence",
        "self-harm"
    ]

    def __init__(self, api_key: Optional[str] = None, strict_mode: bool = True):
        """
        Initialize OpenAI moderator.

        Args:
            api_key: OpenAI API key (default from env)
            strict_mode: If True, use stricter thresholds
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        self.client = AsyncOpenAI(api_key=api_key)
        self.strict_mode = strict_mode

    async def moderate(self, text: str) -> ModerationResult:
        """
        Moderate content using OpenAI Moderation API.

        Args:
            text: Content to moderate

        Returns:
            ModerationResult with flagging details
        """
        response = await self.client.moderations.create(input=text)
        result = response.results[0]

        # Extract categories and scores
        categories = result.categories.model_dump()
        category_scores = result.category_scores.model_dump()

        is_flagged = result.flagged

        # Determine blocking reason
        blocked_reason = None
        if is_flagged:
            # Check critical categories first
            for cat in self.CRITICAL_CATEGORIES:
                if categories.get(cat, False):
                    blocked_reason = f"Critical violation: {cat}"
                    break

            # If no critical, find highest scoring category
            if not blocked_reason:
                primary_violation = max(
                    ((cat, score) for cat, score in category_scores.items() if categories.get(cat, False)),
                    key=lambda x: x[1],
                    default=(None, 0)
                )
                if primary_violation[0]:
                    blocked_reason = f"Policy violation: {primary_violation[0]}"

        return ModerationResult(
            is_flagged=is_flagged,
            categories=categories,
            category_scores=category_scores,
            blocked_reason=blocked_reason
        )

    def is_critical_violation(self, result: ModerationResult) -> bool:
        """Check if result contains critical violations."""
        return any(
            result.categories.get(cat, False)
            for cat in self.CRITICAL_CATEGORIES
        )
