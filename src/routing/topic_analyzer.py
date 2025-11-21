"""Topic analysis for character routing."""

import re
from typing import Dict, List, Tuple


class TopicAnalyzer:
    """Analyze user messages to determine appropriate character."""

    # Topic keywords for each character
    BOTAN_KEYWORDS = [
        # Streaming & content
        "stream", "streaming", "twitch", "youtube", "content", "creator",
        "video", "vtuber", "virtual", "avatar",
        # Social media
        "twitter", "instagram", "tiktok", "social media", "viral", "trending",
        "followers", "likes", "post", "feed",
        # Entertainment
        "movie", "show", "series", "netflix", "anime", "manga",
        "celebrity", "actor", "actress", "entertainment",
        # Pop culture
        "meme", "trend", "popular", "culture", "fashion", "style",
        # Events & social
        "party", "event", "meet", "hangout", "friend", "social"
    ]

    KASHO_KEYWORDS = [
        # Music
        "music", "song", "album", "artist", "band", "guitar", "piano",
        "drum", "instrument", "melody", "rhythm", "chord", "note",
        "compose", "production", "record", "studio", "beat",
        # Career & advice
        "career", "job", "work", "professional", "advice", "help",
        "decision", "choose", "problem", "solve", "relationship",
        "love", "dating", "breakup", "friend", "family",
        # Life planning
        "goal", "plan", "future", "grow", "improve", "develop",
        "success", "balance", "stress", "worry", "concern"
    ]

    YURI_KEYWORDS = [
        # Literature
        "book", "read", "novel", "story", "author", "writer", "literature",
        "fiction", "poetry", "poem", "write", "writing",
        # Sci-fi & fantasy
        "science fiction", "sci-fi", "fantasy", "dragon", "magic",
        "space", "alien", "future", "dystopia", "utopia",
        # Philosophy & deep topics
        "philosophy", "meaning", "existence", "why", "purpose",
        "think", "thought", "idea", "concept", "theory",
        # Creative & subculture
        "creative", "imagination", "indie", "underground", "alternative",
        "art", "artistic", "experimental", "unique", "weird"
    ]

    def __init__(self):
        """Initialize topic analyzer."""
        # Compile keyword patterns for faster matching
        self.botan_pattern = self._compile_pattern(self.BOTAN_KEYWORDS)
        self.kasho_pattern = self._compile_pattern(self.KASHO_KEYWORDS)
        self.yuri_pattern = self._compile_pattern(self.YURI_KEYWORDS)

    def _compile_pattern(self, keywords: List[str]) -> re.Pattern:
        """Compile keyword list into regex pattern."""
        # Escape special characters and join with OR
        escaped = [re.escape(kw) for kw in keywords]
        pattern = r'\b(' + '|'.join(escaped) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    def analyze(self, message: str) -> Dict[str, float]:
        """
        Analyze message and return character scores.

        Args:
            message: User's message

        Returns:
            Dict with character names as keys and scores as values
        """
        message_lower = message.lower()

        # Count keyword matches for each character
        botan_matches = len(self.botan_pattern.findall(message_lower))
        kasho_matches = len(self.kasho_pattern.findall(message_lower))
        yuri_matches = len(self.yuri_pattern.findall(message_lower))

        # Calculate scores (normalize by message length to prevent bias)
        word_count = len(message.split())
        if word_count == 0:
            word_count = 1

        scores = {
            "botan": botan_matches / word_count,
            "kasho": kasho_matches / word_count,
            "yuri": yuri_matches / word_count
        }

        # Apply bonuses for strong indicators
        self._apply_bonuses(message_lower, scores)

        return scores

    def _apply_bonuses(self, message: str, scores: Dict[str, float]) -> None:
        """Apply bonus scores for strong topic indicators."""

        # Botan bonuses
        if any(word in message for word in ["vtuber", "streaming", "viral", "trending"]):
            scores["botan"] += 0.5

        # Kasho bonuses
        if any(word in message for word in ["music", "advice", "help me", "what should i"]):
            scores["kasho"] += 0.5

        # Yuri bonuses
        if any(word in message for word in ["book", "philosophy", "why", "meaning"]):
            scores["yuri"] += 0.5

        # Question patterns
        if message.startswith(("what", "how", "why", "when", "where")):
            # "Why" questions are more philosophical (Yuri)
            if message.startswith("why"):
                scores["yuri"] += 0.3
            # "How" questions about career/life (Kasho)
            elif message.startswith("how") and any(w in message for w in ["should", "can i", "do i"]):
                scores["kasho"] += 0.3

    def select_character(
        self,
        message: str,
        current_character: str = "botan",
        threshold: float = 0.3
    ) -> Tuple[str, Dict[str, float]]:
        """
        Select the best character for responding.

        Args:
            message: User's message
            current_character: Currently active character
            threshold: Minimum score difference to trigger character switch

        Returns:
            Tuple of (selected_character, scores)
        """
        scores = self.analyze(message)

        # Find character with highest score
        best_character = max(scores.items(), key=lambda x: x[1])

        # Switch only if the best character's score is significantly higher
        if best_character[1] > scores[current_character] + threshold:
            return best_character[0], scores
        else:
            # Keep current character (continuity)
            return current_character, scores
