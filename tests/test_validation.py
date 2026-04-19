import pytest
from src.utils.validators import validate_user_text, validate_image_dimensions, ValidationError


def test_validate_user_text_valid():
    assert validate_user_text("hello world") == "hello world"
    assert validate_user_text("  樱花飘落  ") == "樱花飘落"


def test_validate_user_text_too_short():
    with pytest.raises(ValidationError):
        validate_user_text("")
    with pytest.raises(ValidationError):
        validate_user_text("   ")


def test_validate_user_text_too_long():
    long_text = "a" * 600
    with pytest.raises(ValidationError):
        validate_user_text(long_text)


def test_validate_image_dimensions_valid():
    # Should not raise
    validate_image_dimensions(1024, 1024)
    validate_image_dimensions(512, 512)
    validate_image_dimensions(2048, 2048)


def test_validate_image_dimensions_invalid():
    with pytest.raises(ValidationError):
        validate_image_dimensions(200, 1024)
    with pytest.raises(ValidationError):
        validate_image_dimensions(1024, 300)
    with pytest.raises(ValidationError):
        validate_image_dimensions(3000, 1024)
