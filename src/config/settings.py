from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Doubao API Configuration (ByteDance Volces Ark)
    doubao_api_key: str
    # Base URL for chat completion (coding)
    doubao_chat_base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v3"
    # Base URL for image generation
    doubao_image_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    # Model/Endpoint for chat/prompt enhancement
    doubao_chat_model: str = "doubao-seed-2.0-pro"
    # Model/Endpoint for text-to-image generation
    doubao_image_model: str = "doubao-seedream-5-0-260128"

    # Output Configuration
    output_dir: str = "./outputs"

    # Image generation (configurable)
    # API requires at least ~3.68 million pixels (3686400)
    default_image_width: int = 1920
    default_image_height: int = 1920

    # Text rendering defaults
    default_font_size: int = 48
    default_text_color: str = "#ffffff"
    default_stroke_color: str = "#000000"
    default_stroke_width: int = 3
    default_padding: int = 40
    default_gradient_opacity: float = 0.4
    default_text_position: str = "bottom"  # bottom, top, center, auto

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
