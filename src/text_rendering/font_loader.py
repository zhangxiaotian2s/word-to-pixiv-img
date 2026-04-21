import os
from pathlib import Path
from typing import Optional, Dict
from PIL import ImageFont

from src.models.types import FontLoadError
from src.text_rendering.font_selector import AutoFontSelector
from src.utils.logging import logger


class FontLoader:
    """Font loader with fallback chain for cross-platform CJK support.

    Priority:
    1. Explicit font filename in ./fonts/ directory (for auto-selection)
    2. Custom fonts in ./fonts/ directory
    3. System CJK fonts (Noto Sans CJK, Microsoft YaHei, etc.)
    4. Default PIL font
    """

    # Common CJK font paths by platform
    SYSTEM_FONT_PATHS = [
        # Windows
        "C:/Windows/Fonts/msyh.ttc",  # Microsoft YaHei
        "C:/Windows/Fonts/msyhbd.ttc",  # Microsoft YaHei Bold
        "C:/Windows/Fonts/NotoSansCJKtc-Regular.otf",
        "C:/Windows/Fonts/NotoSansCJKsc-Regular.otf",
        "C:/Windows/Fonts/simhei.ttf",  # SimHei
        # macOS
        "/Library/Fonts/Noto Sans CJK SC Regular.ttc",
        "/Library/Fonts/Noto Sans CJK JP Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        # Linux
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]

    def __init__(self, custom_fonts_dir: Path = Path("./fonts/")):
        self.custom_fonts_dir = custom_fonts_dir
        self.auto_selector = AutoFontSelector()
        self._cache: Dict[tuple, ImageFont.FreeTypeFont] = {}

    def get_font_for_text(self, text: str, size: int) -> ImageFont.FreeTypeFont:
        """Automatically select the best font based on text mood.

        Args:
            text: The text to analyze
            size: Font size in pixels

        Returns:
            Best matching font
        """
        font_filename = self.auto_selector.get_font_filename(text)
        if font_filename:
            logger.info(f"Auto-selected font '{font_filename}' for '{text[:30]}...'")
        else:
            logger.info(f"No matching font found for '{text[:30]}...', using fallback")
        return self.get_font(size, font_filename)

    def get_font(self, size: int, font_filename: Optional[str] = None) -> ImageFont.FreeTypeFont:
        """Get font with fallback mechanism.

        Args:
            size: Font size in pixels
            font_filename: Optional font filename in fonts/ directory

        Returns:
            PIL ImageFont object

        Raises:
            FontLoadError: If no font can be loaded
        """
        # Check cache
        cache_key = (font_filename, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        font = self._load_font(font_filename, size)
        self._cache[cache_key] = font
        return font

    def _load_font(self, font_filename: Optional[str], size: int) -> ImageFont.FreeTypeFont:
        """Internal method to try loading font with fallbacks."""

        # 1. Try specific filename in fonts/ directory if provided
        if font_filename:
            font_path = self.custom_fonts_dir / font_filename
            if font_path.exists():
                try:
                    font = ImageFont.truetype(str(font_path), size)
                    logger.info(f"Loaded custom font by filename: {font_path}")
                    return font
                except Exception as e:
                    logger.warning(f"Failed to load font {font_path}: {e}")

        # 2. Try all custom fonts in fonts/ directory
        if self.custom_fonts_dir.exists():
            for ext in [".ttf", ".ttc", ".otf"]:
                for font_file in self.custom_fonts_dir.glob(f"**/*{ext}"):
                    try:
                        font = ImageFont.truetype(str(font_file), size)
                        logger.info(f"Loaded custom font: {font_file}")
                        return font
                    except Exception:
                        continue

        # 3. Try system fonts
        for font_path in self.SYSTEM_FONT_PATHS:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, size)
                    logger.info(f"Loaded system font: {font_path}")
                    return font
                except Exception:
                    continue

        # 4. Fallback to default
        try:
            logger.warning("No custom or system font found, using default PIL font")
            return ImageFont.load_default(size)
        except Exception as e:
            raise FontLoadError(f"Failed to load any font: {e}") from e

    def list_available_fonts(self) -> dict:
        """List all available font categories."""
        return self.auto_selector.list_available_fonts()
