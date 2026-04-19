from PIL import Image

from src.api.doubao_client import DoubaoClient
from src.config.settings import settings
from src.utils.image_utils import bytes_to_image
from src.utils.logging import logger
from src.utils.validators import validate_image_dimensions


class ImageGenerator:
    """Generate anime background image from enhanced prompt using Doubao API."""

    DEFAULT_STYLE_SUFFIX = ", 2D anime style, high quality, detailed background, Pixiv art"

    def __init__(
        self,
        doubao_client: DoubaoClient,
        default_width: Optional[int] = None,
        default_height: Optional[int] = None,
        add_style_suffix: bool = True,
    ):
        self.doubao_client = doubao_client
        self.default_width = default_width or settings.default_image_width
        self.default_height = default_height or settings.default_image_height
        self.add_style_suffix = add_style_suffix

        # Validate default dimensions
        validate_image_dimensions(self.default_width, self.default_height)

    def generate(
        self,
        prompt: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Image.Image:
        """Generate image from enhanced prompt.

        Args:
            prompt: Enhanced prompt
            width: Optional custom width
            height: Optional custom height

        Returns:
            PIL Image object
        """
        w = width or self.default_width
        h = height or self.default_height

        validate_image_dimensions(w, h)

        # Add style keywords if enabled
        if self.add_style_suffix and not prompt.endswith(self.DEFAULT_STYLE_SUFFIX):
            full_prompt = prompt + self.DEFAULT_STYLE_SUFFIX
        else:
            full_prompt = prompt

        logger.info(f"Generating image with prompt: {full_prompt[:100]}...")
        image_bytes = self.doubao_client.text_to_image(full_prompt, width=w, height=h)
        image = bytes_to_image(image_bytes)

        logger.info(f"Image generated: {image.width}x{image.height}")
        return image
