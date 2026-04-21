from pathlib import Path
from typing import Optional
from PIL import Image

from src.config.settings import settings
from src.api.doubao_client import DoubaoClient
from src.core.prompt_enhancer import PromptEnhancer
from src.core.image_generator import ImageGenerator
from src.text_rendering.text_adder import TextAdder
from src.text_rendering.font_loader import FontLoader
from src.models.types import GenerationResult, TextStyle
from src.utils.validators import validate_user_text
from src.utils.image_utils import save_image
from src.utils.logging import logger


class AnimeBackgroundPipeline:
    """
    Main pipeline that orchestrates the full process:
    1. Validate user input
    2. Enhance prompt with Doubao LLM (doubao-seed-2.0-pro)
    3. Generate image with Doubao text-to-image (doubao-seedream-5-0-260128)
    4. Add text overlay with Pillow
    5. Save and return result
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        chat_base_url: Optional[str] = None,
        image_base_url: Optional[str] = None,
        chat_model: Optional[str] = None,
        image_model: Optional[str] = None,
    ):
        # Use settings if not provided explicitly
        api_key = api_key or settings.doubao_api_key
        chat_base_url = chat_base_url or settings.doubao_chat_base_url
        image_base_url = image_base_url or settings.doubao_image_base_url
        chat_model = chat_model or settings.doubao_chat_model
        image_model = image_model or settings.doubao_image_model

        # Initialize components
        self.doubao_client = DoubaoClient(
            api_key=api_key,
            chat_base_url=chat_base_url,
            image_base_url=image_base_url,
            chat_model=chat_model,
            image_model=image_model,
        )
        self.prompt_enhancer = PromptEnhancer(self.doubao_client)
        self.image_generator = ImageGenerator(
            self.doubao_client,
            settings.default_image_width,
            settings.default_image_height
        )
        self.font_loader = FontLoader()
        self.text_adder = TextAdder(self.font_loader)

        logger.info("AnimeBackgroundPipeline initialized")

    def generate(
        self,
        user_text: str,
        auxiliary_text: Optional[str] = None,
        text_style: Optional[TextStyle] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        save_output: bool = True,
        output_dir: Optional[Path] = None,
    ) -> GenerationResult:
        """Run the full generation pipeline.

        Args:
            user_text: User input text (displayed on image)
            auxiliary_text: Optional auxiliary context to guide image generation (not displayed)
            text_style: Optional custom text style
            width: Optional custom image width
            height: Optional custom image height
            save_output: Whether to save the output image
            output_dir: Output directory (defaults to settings)

        Returns:
            GenerationResult with all metadata
        """
        try:
            # Step 1: Validate input
            logger.info(f"Starting generation for text: {user_text[:50]}...")
            cleaned_text = validate_user_text(user_text)

            # Step 2: Enhance prompt (with auxiliary text if provided)
            enhanced_prompt = self.prompt_enhancer.enhance(cleaned_text, auxiliary_text)

            # Step 3: Generate image
            if width and height:
                image = self.image_generator.generate(enhanced_prompt, width, height)
            else:
                image = self.image_generator.generate(enhanced_prompt)

            # Step 4: Add text overlay
            if text_style is None:
                text_style = TextStyle()
            final_image = self.text_adder.add_text(image, cleaned_text, text_style)

            # Step 5: Save if requested
            image_path = None
            if save_output:
                image_path = save_image(final_image, cleaned_text, output_dir)
                logger.info(f"Final image saved to {image_path}")

            return GenerationResult(
                original_text=cleaned_text,
                auxiliary_text=auxiliary_text,
                enhanced_prompt=enhanced_prompt,
                image_path=image_path,
                success=True,
            )

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            return GenerationResult(
                original_text=user_text,
                auxiliary_text=auxiliary_text,
                enhanced_prompt="",
                success=False,
                error_message=str(e),
            )
