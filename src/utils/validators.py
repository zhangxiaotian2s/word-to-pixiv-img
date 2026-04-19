import re
from typing import Optional

from src.models.types import ValidationError


MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 500
MIN_IMAGE_DIMENSION = 512
MAX_IMAGE_DIMENSION = 2560
# Doubao API requires at least 3.68 million pixels (3686400)
MIN_TOTAL_PIXELS = 3686400


def validate_user_text(text: str) -> str:
    """Validate user input text.

    Args:
        text: User input text

    Returns:
        Cleaned and validated text

    Raises:
        ValidationError: If text is invalid
    """
    text = text.strip()

    if len(text) < MIN_TEXT_LENGTH:
        raise ValidationError(
            f"Text too short. Minimum length is {MIN_TEXT_LENGTH} character."
        )

    if len(text) > MAX_TEXT_LENGTH:
        raise ValidationError(
            f"Text too long. Maximum length is {MAX_TEXT_LENGTH} characters."
        )

    # Basic sanitization to prevent any problematic characters
    # Remove any control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    return text


def validate_image_dimensions(width: int, height: int) -> None:
    """Validate image dimensions are within acceptable ranges.

    Args:
        width: Image width
        height: Image height

    Raises:
        ValidationError: If dimensions are invalid
    """
    if width < MIN_IMAGE_DIMENSION:
        raise ValidationError(
            f"Width {width} too small. Minimum is {MIN_IMAGE_DIMENSION}px."
        )
    if height < MIN_IMAGE_DIMENSION:
        raise ValidationError(
            f"Height {height} too small. Minimum is {MIN_IMAGE_DIMENSION}px."
        )
    if width > MAX_IMAGE_DIMENSION:
        raise ValidationError(
            f"Width {width} too large. Maximum is {MAX_IMAGE_DIMENSION}px."
        )
    if height > MAX_IMAGE_DIMENSION:
        raise ValidationError(
            f"Height {height} too large. Maximum is {MAX_IMAGE_DIMENSION}px."
        )

    total_pixels = width * height
    if total_pixels < MIN_TOTAL_PIXELS:
        raise ValidationError(
            f"Image size too small. Total pixels must be at least {MIN_TOTAL_PIXELS} (e.g. 1920x1920, 1440x2560). Got {total_pixels} pixels for {width}x{height}."
        )


def validate_prompt(prompt: str) -> str:
    """Validate enhanced prompt before image generation.

    Args:
        prompt: Enhanced prompt from LLM

    Returns:
        Cleaned prompt

    Raises:
        ValidationError: If prompt is empty
    """
    prompt = prompt.strip()
    if not prompt:
        raise ValidationError("Enhanced prompt is empty.")

    # Remove any markdown code blocks or explanations that might have been included
    # Strip any leading/trailing explanations
    prompt = re.sub(r'^.*(Enhanced prompt:|Prompt:|Here is the prompt)', '', prompt, flags=re.IGNORECASE)
    prompt = re.sub(r'```.*?```', '', prompt, flags=re.DOTALL)
    prompt = prompt.strip()

    return prompt
