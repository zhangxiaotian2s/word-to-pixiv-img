from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Custom Exceptions
class WordToPixivError(Exception):
    """Base exception for this project"""
    pass


class ConfigurationError(WordToPixivError):
    """Configuration related error"""
    pass


class ValidationError(WordToPixivError):
    """Input validation error"""
    pass


class APIError(WordToPixivError):
    """API call error"""
    pass


class ImageGenerationError(WordToPixivError):
    """Image generation error"""
    pass


class FontLoadError(WordToPixivError):
    """Font loading error"""
    pass


@dataclass
class TextStyle:
    """Text style configuration for overlay"""
    font_path: Optional[str] = None
    font_size: Optional[int] = None
    text_color: str = "#ffffff"
    stroke_color: str = "#000000"
    stroke_width: int = 3
    padding: int = 40
    gradient_opacity: float = 0.4
    position: str = "bottom"  # bottom, top, center, auto
    alignment: str = "center"  # left, center, right
    auto_font: bool = True  # Automatically select font based on text mood


@dataclass
class GenerationResult:
    """Result of the full generation pipeline"""
    original_text: str
    enhanced_prompt: str
    image_path: Optional[Path] = None
    success: bool = True
    error_message: Optional[str] = None
