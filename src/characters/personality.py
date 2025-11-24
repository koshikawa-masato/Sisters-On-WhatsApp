"""Character personality management - loads prompts from files."""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List


class CharacterPersonality:
    """Manage character personalities by loading prompts from files."""

    # Character names
    BOTAN = "botan"
    KASHO = "kasho"
    YURI = "yuri"

    ALL_CHARACTERS = [BOTAN, KASHO, YURI]

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize character personality loader.

        Args:
            prompts_dir: Directory containing prompt files (default: project_root/prompts/)
        """
        if prompts_dir is None:
            # Get project root (4 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            prompts_dir = project_root / "prompts"

        self.prompts_dir = prompts_dir
        self._cache: Dict[str, str] = {}
        self.verified_knowledge_file = prompts_dir / "verified_knowledge.json"

        # Verify prompts directory exists
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory not found: {self.prompts_dir}\n"
                "Please ensure character prompt files exist in prompts/ directory."
            )

    def get_system_prompt(self, character: str, user_message: Optional[str] = None) -> str:
        """
        Load system prompt for a character.

        Args:
            character: Character name (botan, kasho, yuri)
            user_message: Optional user message to search for relevant verified facts

        Returns:
            System prompt text (common prompt + character-specific prompt + verified knowledge if relevant)

        Raises:
            ValueError: If character is unknown
            FileNotFoundError: If prompt file doesn't exist
        """
        character = character.lower()

        if character not in self.ALL_CHARACTERS:
            raise ValueError(
                f"Unknown character: {character}. "
                f"Valid options: {', '.join(self.ALL_CHARACTERS)}"
            )

        # Check cache first (only for base prompt without verified knowledge)
        if character not in self._cache:
            # Load common prompt (shared by all sisters)
            common_prompt_file = self.prompts_dir / "common_system_prompt.txt"
            common_prompt = ""

            if common_prompt_file.exists():
                with open(common_prompt_file, 'r', encoding='utf-8') as f:
                    common_prompt = f.read().strip()

            # Load character-specific prompt
            prompt_file = self.prompts_dir / f"{character}_system_prompt.txt"

            if not prompt_file.exists():
                raise FileNotFoundError(
                    f"Prompt file not found: {prompt_file}\n"
                    f"Expected file: {character}_system_prompt.txt"
                )

            with open(prompt_file, 'r', encoding='utf-8') as f:
                character_prompt = f.read().strip()

            # Combine: character-specific first, then common rules
            self._cache[character] = f"{character_prompt}\n\n---\n\n{common_prompt}" if common_prompt else character_prompt

        base_prompt = self._cache[character]

        # Inject verified knowledge if user message provided
        verified_knowledge = self._get_relevant_verified_knowledge(user_message) if user_message else ""

        if verified_knowledge:
            return f"{base_prompt}\n\n---\n\n{verified_knowledge}"
        else:
            return base_prompt

    def _get_relevant_verified_knowledge(self, user_message: str) -> str:
        """
        Search verified knowledge base for facts relevant to user message.

        Args:
            user_message: User's message

        Returns:
            Formatted verified knowledge string (empty if no relevant facts found)
        """
        if not user_message or not self.verified_knowledge_file.exists():
            return ""

        try:
            with open(self.verified_knowledge_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return ""

        # Search all categories for relevant facts
        relevant_facts = []
        user_message_lower = user_message.lower()

        for category, facts in knowledge.items():
            if category == "last_updated":
                continue

            if not isinstance(facts, dict):
                continue

            for name, data in facts.items():
                # Check if name appears in user message
                if name.lower() in user_message_lower:
                    relevant_facts.append({
                        "name": name,
                        "category": category,
                        "details": data.get("details", {}),
                        "confidence": data.get("confidence", 0.0)
                    })

        if not relevant_facts:
            return ""

        # Format verified knowledge for injection
        knowledge_text = "## VERIFIED KNOWLEDGE (from past conversations)\n\n"
        knowledge_text += "The following facts have been verified with high confidence. You can reference them confidently:\n\n"

        for fact in relevant_facts:
            knowledge_text += f"**{fact['name']}** ({fact['category']}):\n"

            details = fact['details']
            if details.get('location'):
                knowledge_text += f"  - Location: {details['location']}\n"
            if details.get('type'):
                knowledge_text += f"  - Type: {details['type']}\n"
            if details.get('specialties'):
                specialties = ', '.join(details['specialties'])
                knowledge_text += f"  - Known for: {specialties}\n"
            if details.get('notes'):
                knowledge_text += f"  - Notes: {details['notes']}\n"

            knowledge_text += f"  - Confidence: {fact['confidence']:.0%}\n\n"

        return knowledge_text

    def reload_prompts(self) -> None:
        """Clear cache and reload all prompts from files."""
        self._cache.clear()

    def get_character_display_name(self, character: str) -> str:
        """Get display name for a character."""
        names = {
            self.BOTAN: "Botan 🌸",
            self.KASHO: "Kasho 🎵",
            self.YURI: "Yuri 📚"
        }
        return names.get(character.lower(), character.capitalize())

    def get_character_description(self, character: str) -> str:
        """Get short description of a character."""
        descriptions = {
            self.BOTAN: "Social media enthusiast and entertainment expert",
            self.KASHO: "Music professional and life advisor",
            self.YURI: "Book lover and creative thinker"
        }
        return descriptions.get(character.lower(), "")
