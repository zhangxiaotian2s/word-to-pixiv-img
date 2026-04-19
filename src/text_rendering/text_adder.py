import math
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageColor

from src.config.settings import settings
from src.models.types import TextStyle
from src.text_rendering.font_loader import FontLoader
from src.utils.image_utils import calculate_average_brightness
from src.utils.logging import logger


class TextAdder:
    """Add text overlay to image with elegant typography and readability guarantees.

    Implements multiple layers of readability:
    1. Semi-transparent gradient background
    2. Text stroke (outline)
    3. Drop shadow
    4. Automatic text wrapping
    5. Smart position selection (optional)
    """

    def __init__(self, font_loader: Optional[FontLoader] = None):
        self.font_loader = font_loader or FontLoader()

    @staticmethod
    def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple."""
        rgb = ImageColor.getcolor(hex_color, "RGB")
        return (*rgb, int(255 * alpha))

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
    ) -> List[str]:
        """Wrap text to fit within max_width.

        Args:
            text: Text to wrap
            font: Font object
            max_width: Maximum width in pixels

        Returns:
            List of lines
        """
        # Split by newlines first
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current_line = words[0]
            for word in words[1:]:
                test_line = current_line + " " + word
                bbox = font.getbbox(test_line)
                w = bbox[2] - bbox[0]
                if w <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

        return lines

    def _calculate_text_metrics(
        self,
        lines: List[str],
        font: ImageFont.FreeTypeFont,
        line_spacing: float = 1.3,
    ) -> Tuple[int, int, int]:
        """Calculate total width, total height, and max line height.

        Returns:
            (total_width, total_height, line_height)
        """
        max_width = 0
        total_height = 0
        ascent, descent = font.getmetrics()
        line_height = (ascent + descent) * line_spacing

        for line in lines:
            bbox = font.getbbox(line)
            w = bbox[2] - bbox[0]
            max_width = max(max_width, w)
            total_height += line_height

        total_height -= (line_spacing - 1.0) * line_height  # Remove extra spacing after last line
        return int(max_width), int(math.ceil(total_height)), int(math.ceil(line_height))

    def _find_best_region(
        self,
        image: Image.Image,
        text_height: int,
        padding: int,
    ) -> str:
        """Find the best region for text by analyzing brightness uniformity.

        The image is split into 3 horizontal regions (top, middle, bottom).
        We choose the region with lowest entropy/best contrast.

        Returns:
            "top", "middle", or "bottom"
        """
        w, h = image.size
        region_height = text_height + padding * 2

        regions = []

        # Bottom region
        bottom_y1 = h - region_height
        bottom_brightness = calculate_average_brightness(image, (0, bottom_y1, w, h))
        # We want moderate brightness - not too dark (for white text) not too bright
        bottom_score = abs(bottom_brightness - 128)
        regions.append((bottom_score, "bottom"))

        # Top region
        top_y2 = region_height
        top_brightness = calculate_average_brightness(image, (0, 0, w, top_y2))
        top_score = abs(top_brightness - 128)
        regions.append((top_score, "top"))

        # Middle region
        middle_y1 = (h - region_height) // 2
        middle_y2 = middle_y1 + region_height
        middle_brightness = calculate_average_brightness(image, (0, middle_y1, w, middle_y2))
        middle_score = abs(middle_brightness - 128)
        regions.append((middle_score, "middle"))

        # Pick region with lowest score (closest to 128 brightness)
        regions.sort(key=lambda x: x[0])
        best = regions[0][1]
        logger.debug(f"Smart position selected: {best} (scores: {[s[0] for s in regions]})")
        return best

    def _get_y_position(
        self,
        image_height: int,
        text_total_height: int,
        padding: int,
        position_mode: str,
        text_height_for_analysis: int,
        image: Image.Image,
    ) -> int:
        """Get starting Y coordinate for text based on position mode."""
        if position_mode == "auto":
            position_mode = self._find_best_region(image, text_height_for_analysis, padding)

        if position_mode == "bottom":
            return image_height - text_total_height - padding
        elif position_mode == "top":
            return padding
        elif position_mode == "center":
            return (image_height - text_total_height) // 2
        else:  # bottom default
            return image_height - text_total_height - padding

    def add_text(
        self,
        image: Image.Image,
        text: str,
        style: Optional[TextStyle] = None,
    ) -> Image.Image:
        """Add text overlay to image.

        Args:
            image: Input PIL Image
            text: Text to add
            style: Text style configuration (uses defaults if not provided)

        Returns:
            New image with text added
        """
        style = style or TextStyle()

        # Get defaults from settings are overridden
        font_size = style.font_size or settings.default_font_size
        text_color = self._hex_to_rgba(style.text_color or settings.default_text_color)
        stroke_color = self._hex_to_rgba(style.stroke_color or settings.default_stroke_color)
        stroke_width = style.stroke_width or settings.default_stroke_width
        padding = style.padding or settings.default_padding
        gradient_opacity = style.gradient_opacity or settings.default_gradient_opacity
        position = style.position or settings.default_text_position
        alignment = style.alignment or "center"

        # Load font - if auto_font is True, automatically select based on text mood
        if style.auto_font:
            font = self.font_loader.get_font_for_text(text, font_size)
        else:
            font = self.font_loader.get_font(font_size, style.font_path)

        # Work on copy
        result = image.copy()
        draw = ImageDraw.Draw(result)
        w, h = result.size

        # Calculate maximum text width
        max_text_width = w - padding * 2

        # Wrap text
        lines = self._wrap_text(text, font, max_text_width)
        text_width, text_total_height, line_height = self._calculate_text_metrics(lines, font)

        # Get starting Y position
        y_start = self._get_y_position(
            h, text_total_height, padding, position,
            text_total_height, result
        )

        # Create semi-transparent gradient background
        if gradient_opacity > 0:
            gradient_h = text_total_height + padding * 2
            gradient_y = y_start - padding
            gradient = Image.new("RGBA", (w, gradient_h))
            gradient_draw = ImageDraw.Draw(gradient)

            # Gradient from 0 opacity to full opacity going down for bottom position
            # Going up for top/center position
            if position == "bottom" or position == "auto":
                start_alpha = 0
                end_alpha = gradient_opacity
            else:
                start_alpha = gradient_opacity
                end_alpha = 0

            # Draw vertical gradient
            for y in range(gradient_h):
                alpha = int(255 * (start_alpha + (end_alpha - start_alpha) * y / gradient_h))
                gradient_draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha), width=1)

            result.paste(gradient, (0, gradient_y), gradient)

        # Draw text with stroke
        for line in lines:
            # Calculate X position based on alignment
            line_bbox = font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            if alignment == "center":
                x = (w - line_width) // 2
            elif alignment == "left":
                x = padding
            else:  # right
                x = w - line_width - padding

            # Draw stroke (outline) by drawing text in all directions
            # This is the standard way to do stroke in PIL
            for dx in [-stroke_width, 0, stroke_width]:
                for dy in [-stroke_width, 0, stroke_width]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y_start + dy), line, font=font, fill=stroke_color)

            # Draw main text
            draw.text((x, y_start), line, font=font, fill=text_color)

            # Move to next line
            y_start += line_height

        logger.debug(f"Added text '{text[:30]}...' with {len(lines)} lines")
        return result
