from typing import Optional

from src.api.doubao_client import DoubaoClient
from src.utils.logging import logger
from src.utils.validators import validate_prompt


class PromptEnhancer:
    """Enhance user text into high-quality anime background prompt for AI image generation."""

    # System prompt that instructs the model to create a good prompt
    DEFAULT_SYSTEM_PROMPT = """You are a prompt engineer specialized for 2D anime-style background image generation.

Given the user's simple caption or phrase, convert it into a detailed, high-quality prompt for AI image generation.
The final image should be a beautiful 2D anime background, no characters needed (unless user mentions characters).

Guidelines:
- Focus on the user's core topic: {user_text}
- Describe the scene in detail: location, environment, weather, time of day
- Add art style keywords: 2D anime, high detail, digital art, Pixiv style, high quality
- Add lighting information: soft daylight, golden hour, moody night, rim lighting, etc.
- Add composition: wide shot, background, atmospheric perspective, detailed background
- Describe color palette and overall atmosphere
- Keep the prompt cohesive and natural, around 50-100 words
- Output ONLY the enhanced prompt text, no explanations, no introductions, no extra commentary.

Enhanced prompt:"""

    def __init__(self, doubao_client: DoubaoClient, system_prompt: Optional[str] = None):
        self.doubao_client = doubao_client
        self.system_prompt_template = system_prompt or self.DEFAULT_SYSTEM_PROMPT

    def enhance(self, user_text: str) -> str:
        """Enhance user text to high-quality anime prompt.

        Args:
            user_text: User input text

        Returns:
            Enhanced prompt ready for image generation
        """
        system_prompt = self.system_prompt_template.format(user_text=user_text)
        logger.info(f"Enhancing prompt for: {user_text[:50]}...")

        enhanced_prompt = self.doubao_client.chat_completion(
            system_prompt=system_prompt,
            user_message=user_text,
        )

        # Clean and validate
        enhanced_prompt = validate_prompt(enhanced_prompt)
        logger.info(f"Enhanced prompt: {enhanced_prompt}")

        return enhanced_prompt
