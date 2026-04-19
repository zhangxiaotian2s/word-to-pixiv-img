"""
Test text rendering without requiring API calls.
We create a simple test image and test text wrapping and placement.
"""
import pytest
from PIL import Image

from src.text_rendering.text_adder import TextAdder
from src.text_rendering.font_loader import FontLoader
from src.models.types import TextStyle


def test_add_text_basic():
    """Test basic text addition works."""
    # Create a blank image
    image = Image.new("RGB", (1024, 1024), color=(100, 100, 200))

    font_loader = FontLoader()
    text_adder = TextAdder(font_loader)

    style = TextStyle(position="bottom")
    result = text_adder.add_text(image, "测试文字", style)

    assert result.size == (1024, 1024)
    assert result.mode == "RGB"


def test_add_text_multiline():
    """Test text wrapping for longer text."""
    image = Image.new("RGB", (1024, 1024), color=(100, 100, 200))

    font_loader = FontLoader()
    text_adder = TextAdder(font_loader)

    long_text = "这是一段比较长的文字 应该会自动换行 让我们看看是否正确分成多行显示"
    style = TextStyle(position="center")
    result = text_adder.add_text(image, long_text, style)

    assert result.size == (1024, 1024)


def test_different_positions():
    """Test different position modes work."""
    image = Image.new("RGB", (1024, 1024))
    text_adder = TextAdder()

    for position in ["bottom", "top", "center"]:
        style = TextStyle(position=position)
        result = text_adder.add_text(image, "测试", style)
        assert result.size == (1024, 1024)


@pytest.mark.e2e
def test_smart_position():
    """Test smart position selection."""
    # Create image with dark bottom
    image = Image.new("RGB", (1024, 1024), color=(255, 255, 255))
    for y in range(700, 1024):
        for x in range(1024):
            image.putpixel((x, y), (0, 0, 0))

    text_adder = TextAdder()
    style = TextStyle(position="auto")
    result = text_adder.add_text(image, "测试文字", style)
    assert result.size == (1024, 1024)
