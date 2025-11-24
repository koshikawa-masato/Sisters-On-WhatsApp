"""Character personality management - loads prompts from files."""

import os
from pathlib import Path
from typing import Dict, Optional


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

        # Verify prompts directory exists
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory not found: {self.prompts_dir}\n"
                "Please ensure character prompt files exist in prompts/ directory."
            )

    def get_system_prompt(self, character: str) -> str:
        """
        Load system prompt for a character.

        Args:
            character: Character name (botan, kasho, yuri)

        Returns:
            System prompt text (common prompt + character-specific prompt)

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

        # Check cache first
        if character in self._cache:
            return self._cache[character]

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
        prompt = f"{character_prompt}\n\n---\n\n{common_prompt}" if common_prompt else character_prompt

        # Cache for future use
        self._cache[character] = prompt

        return prompt

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
