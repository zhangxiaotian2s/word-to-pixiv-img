import io
from datetime import datetime
from pathlib import Path
from typing import Optional
from PIL import Image

from src.config.settings import settings


def generate_unique_filename(text: str, extension: str = "png") -> str:
    """Generate a unique filename based on input text and timestamp.

    Args:
        text: Input text to include in filename
        extension: File extension

    Returns:
        Unique filename
    """
    # Take first 30 characters of text, replace spaces and special chars
    clean_text = "".join(c if c.isalnum() else "_" for c in text[:30]).strip("_")
    if not clean_text:
        clean_text = "output"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{clean_text}_{timestamp}.{extension}"


def save_image(
    image: Image.Image,
    text: str,
    output_dir: Optional[Path] = None,
    quality: int = 95
) -> Path:
    """Save PIL image to output directory with unique filename.

    Args:
        image: PIL Image to save
        text: Input text for filename
        output_dir: Output directory (defaults to settings.output_dir)
        quality: JPEG/PNG quality

    Returns:
        Path to saved image
    """
    if output_dir is None:
        output_dir = Path(settings.output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = generate_unique_filename(text)
    output_path = output_dir / filename

    image.save(output_path, "PNG", compress_level=6, quality=quality)
    return output_path


def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """Convert bytes from API response to PIL Image.

    Args:
        image_bytes: Raw image bytes from API

    Returns:
        PIL Image
    """
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")


def calculate_average_brightness(image: Image.Image, box: tuple[int, int, int, int]) -> float:
    """Calculate average brightness in a region (0-255).

    Args:
        image: PIL Image (RGB)
        box: (x1, y1, x2, y2) region

    Returns:
        Average brightness 0-255
    """
    x1, y1, x2, y2 = box
    region = image.crop((x1, y1, x2, y2)).convert("L")
    histogram = region.histogram()
    total_pixels = (x2 - x1) * (y2 - y1)
    average = sum(i * count for i, count in enumerate(histogram)) / total_pixels
    return average
