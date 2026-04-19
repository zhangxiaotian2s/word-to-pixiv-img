import json
from typing import Any, Dict, Optional

from src.api.base import BaseAPIClient
from src.models.types import APIError, ImageGenerationError
from src.utils.logging import logger


class DoubaoClient:
    """Doubao API client for ByteDance Volces Ark.

    Supports two operations:
    1. Chat completion for prompt enhancement (uses doubao-seed-2.0-pro at /api/coding/v3)
    2. Text-to-image generation (uses doubao-seedream-5-0-260128 at /api/v3)
    """

    def __init__(
        self,
        api_key: str,
        chat_base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v3",
        image_base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        chat_model: str = "doubao-seed-2.0-pro",
        image_model: str = "doubao-seedream-5-0-260128",
        max_retries: int = 3,
        timeout: int = 180,  # Longer timeout for image generation
    ):
        self.chat_client = BaseAPIClient(chat_base_url, api_key, max_retries=max_retries, timeout=timeout)
        self.image_client = BaseAPIClient(image_base_url, api_key, max_retries=max_retries, timeout=timeout)
        self.chat_model = chat_model
        self.image_model = image_model

    def chat_completion(self, system_prompt: str, user_message: str) -> str:
        """Call chat completion for text processing (prompt enhancement).

        Args:
            system_prompt: System instruction
            user_message: User input text

        Returns:
            Model response text

        Raises:
            APIError: If the API call fails
        """
        endpoint = "chat/completions"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        body = {
            "model": self.chat_model,
            "messages": messages,
            "temperature": 0.7,
        }

        response = self.chat_client.post(endpoint, body)
        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Chat completion response: {content[:100]}...")
            return content.strip()
        except (KeyError, IndexError) as e:
            error_msg = f"Failed to parse chat response: {e}, data: {json.dumps(data)}"
            logger.error(error_msg)
            raise APIError(error_msg) from e

    def text_to_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
    ) -> bytes:
        """Generate image from prompt using text-to-image API.

        Following official ByteDance Volces Ark API documentation.

        Args:
            prompt: Image generation prompt
            width: Image width
            height: Image height
            num_images: Number of images to generate

        Returns:
            Raw image bytes

        Raises:
            ImageGenerationError: If generation fails or no image returned
            APIError: If API call fails
        """
        endpoint = "images/generations"

        # Convert size to format expected by API (e.g. "1024x1024")
        size = f"{width}x{height}"

        body = {
            "model": self.image_model,
            "prompt": prompt,
            "size": size,
            "n": num_images,
            "response_format": "url",
            # Disable watermark for cleaner output
            "extra_body": {
                "watermark": False,
            },
        }

        response = self.image_client.post(endpoint, body)
        data = response.json()

        try:
            if "data" in data and len(data["data"]) > 0:
                image_data = data["data"][0]

                # If response contains base64
                if "b64_json" in image_data:
                    import base64
                    return base64.b64decode(image_data["b64_json"])

                # If response contains URL (as in official example)
                if "url" in image_data:
                    image_url = image_data["url"]
                    logger.debug(f"Generated image URL: {image_url}")
                    # Download the image
                    image_response = self.image_client.session.get(image_url, timeout=self.image_client.timeout)
                    image_response.raise_for_status()
                    return image_response.content

            error_msg = f"No image data in response: {json.dumps(data)}"
            logger.error(error_msg)
            raise ImageGenerationError(error_msg)
        except (KeyError, IndexError) as e:
            error_msg = f"Failed to parse image response: {e}, data: {json.dumps(data)}"
            logger.error(error_msg)
            raise ImageGenerationError(error_msg) from e
