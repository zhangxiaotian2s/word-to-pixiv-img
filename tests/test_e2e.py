"""
End-to-end integration test that calls actual APIs.
Only run manually when testing, skipped in CI if no API key.
"""

import pytest
from pathlib import Path

from src.config.settings import settings
from src.core.pipeline import AnimeBackgroundPipeline


@pytest.mark.e2e
@pytest.mark.parametrize(
    "user_text",
    [
        "樱花飘落的公园小路",
        "夕阳下的城市街道",
        "雨夜中的日本车站",
    ]
)
def test_full_pipeline(user_text):
    # Skip if no valid API key
    if not settings.doubao_api_key or len(settings.doubao_api_key) < 20:
        pytest.skip("No valid API key configured for E2E test")

    pipeline = AnimeBackgroundPipeline()
    result = pipeline.generate(user_text=user_text, save_output=True)

    assert result.success
    assert result.image_path is not None
    assert result.image_path.exists()
    assert result.image_path.stat().st_size > 10000  # At least 10KB
    assert len(result.enhanced_prompt) > len(result.original_text)
    print(f"\n✓ Success: {user_text} → {result.image_path}")
