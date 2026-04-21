"""
Font selector that automatically selects appropriate font based on text context/mood.

Scans fonts/ directory and uses filename keywords (like "恋爱或情窦.ttf") to match
against input text. Supports "或" and "与" as separators for multiple keywords per font.
When multiple fonts match, one is selected randomly.
"""

import os
import random
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.utils.logging import logger


class FontEntry:
    """Represents a font file with its mood keywords extracted from filename."""

    def __init__(self, filename: str, keywords: List[str]):
        self.filename = filename
        self.keywords = [kw.lower() for kw in keywords]
        # Extract base name without extension for display
        self.name = Path(filename).stem

    def match_score(self, text: str) -> int:
        """Calculate match score against input text."""
        text_lower = text.lower()
        score = 0
        for keyword in self.keywords:
            if keyword in text_lower:
                score += len(keyword)
        return score


class AutoFontSelector:
    """Automatically select the best font based on text content and mood.

    Scans fonts/ directory and extracts keywords from filenames.
    Filename format: "关键词1或关键词2与关键词3.ttf"
    Supports separators: "或", "与", "、", "/", "|", "and", "or"
    """

    def __init__(self, fonts_dir: Optional[str] = None):
        if fonts_dir is None:
            fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "fonts")
        self.fonts_dir = Path(fonts_dir)
        self.fonts: List[FontEntry] = []
        self._scan_fonts()
        logger.info(f"AutoFontSelector initialized with {len(self.fonts)} fonts from {self.fonts_dir}")

    def _extract_keywords(self, filename: str) -> List[str]:
        """Extract mood keywords from font filename.

        Example:
            "恋爱或情窦.ttf" -> ["恋爱", "情窦"]
            "青春或希望.ttf" -> ["青春", "希望"]
            "悠闲时光.ttf" -> ["悠闲", "时光", "悠闲时光"]
        """
        # Remove file extension
        name = Path(filename).stem

        # Split by common separators
        separators = r"[或与、/|\\]"
        parts = re.split(separators, name)

        # Also add the full name as a keyword
        keywords = set(parts + [name])

        # Remove empty strings and strip whitespace
        keywords = [kw.strip() for kw in keywords if kw.strip()]

        return keywords

    def _scan_fonts(self) -> None:
        """Scan fonts directory and load all font files."""
        self.fonts = []
        seen = set()
        if not self.fonts_dir.exists():
            logger.warning(f"Fonts directory not found: {self.fonts_dir}")
            return

        for font_file in self.fonts_dir.iterdir():
            if font_file.suffix.lower() not in [".ttf", ".otf", ".ttc"]:
                continue
            if font_file.name == ".gitkeep":
                continue
            # Avoid duplicates from case-insensitive matching
            if font_file.name.lower() in seen:
                continue
            seen.add(font_file.name.lower())
            keywords = self._extract_keywords(font_file.name)
            self.fonts.append(FontEntry(font_file.name, keywords))
            logger.debug(f"Loaded font: {font_file.name} with keywords: {keywords}")

        if not self.fonts:
            logger.warning("No font files found in fonts directory")

    def analyze_mood(self, text: str) -> Tuple[List[FontEntry], int]:
        """Analyze text mood and return all matching fonts sorted by score.

        Returns:
            (list_of_matching_fonts, highest_score)
        """
        if not self.fonts:
            return [], 0

        scores: List[Tuple[int, FontEntry]] = []
        for font in self.fonts:
            score = font.match_score(text)
            if score > 0:
                scores.append((score, font))

        # Sort by score descending
        scores.sort(reverse=True, key=lambda x: x[0])

        if not scores:
            logger.debug(f"No mood keywords matched for: {text[:30]}...")
            return [], 0

        highest_score = scores[0][0]
        # Get all fonts with the highest score (best matches)
        best_matches = [font for score, font in scores if score == highest_score]

        logger.debug(f"Mood analysis for '{text[:30]}...': {len(best_matches)} matches (score: {highest_score})")
        return best_matches, highest_score

    def get_font_filename(self, text: str) -> Optional[str]:
        """Get the best matching font filename for given text.

        If multiple fonts match with the same score, randomly select one.
        If no fonts match, returns None (caller should use fallback).
        """
        matches, _ = self.analyze_mood(text)

        if not matches:
            return None

        # Randomly select from best matches
        selected = random.choice(matches)
        logger.debug(f"Selected font '{selected.filename}' for text: {text[:30]}...")
        return selected.filename

    def list_available_fonts(self) -> Dict[str, List[str]]:
        """List all available fonts with their keywords."""
        return {font.filename: font.keywords for font in self.fonts}
