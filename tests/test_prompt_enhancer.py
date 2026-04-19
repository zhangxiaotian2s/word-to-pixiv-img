"""
Test prompt enhancer logic. API is mocked.
"""
import pytest
from unittest.mock import Mock

from src.core.prompt_enhancer import PromptEnhancer


def test_prompt_enhancer_returns_cleaned_prompt():
    """Test prompt enhancer returns cleaned response."""
    mock_client = Mock()
    mock_client.chat_completion.return_value = "beautiful cherry blossom park, spring afternoon, 2D anime style, soft lighting, wide shot"

    enhancer = PromptEnhancer(mock_client)
    result = enhancer.enhance("樱花飘落的公园小路")

    assert "cherry blossom" in result
    assert len(result) > 20
    mock_client.chat_completion.assert_called_once()
