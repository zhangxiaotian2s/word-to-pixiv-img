#!/usr/bin/env python3
"""
Simple CLI example for Word-to-Pixiv Anime Background Generator.

Usage:
    python examples/simple_cli.py "樱花飘落的公园小路 春天"
"""

import click

from src.config.settings import settings
from src.core.pipeline import AnimeBackgroundPipeline
from src.models.types import TextStyle


@click.command()
@click.argument("text")
@click.option(
    "--position", "-p",
    type=click.Choice(["bottom", "top", "center", "auto"]),
    default=None,
    help="Text position (default from settings)",
)
@click.option(
    "--width", "-w",
    type=int,
    default=None,
    help="Image width",
)
@click.option(
    "--height", "-h",
    type=int,
    default=None,
    help="Image height",
)
@click.option(
    "--font-size",
    type=int,
    default=None,
    help="Font size",
)
@click.option(
    "--prompt-only",
    is_flag=True,
    default=False,
    help="Only output enhanced prompt, don't generate image",
)
@click.option(
    "--no-auto-font",
    is_flag=True,
    default=False,
    help="Disable automatic font selection by text mood",
)
def main(
    text: str,
    position: str,
    width: int,
    height: int,
    font_size: int,
    prompt_only: bool,
    no_auto_font: bool,
):
    """Generate anime background image with text overlay.

    TEXT: Your caption/phrase to generate image from
    """
    # Create pipeline
    pipeline = AnimeBackgroundPipeline()

    if prompt_only:
        # Only show enhanced prompt
        from src.core.prompt_enhancer import PromptEnhancer
        enhanced = pipeline.prompt_enhancer.enhance(text)
        click.echo(f"Original: {text}")
        click.echo(f"Enhanced: {enhanced}")
        return

    # Build text style
    text_style = TextStyle(
        position=position,
        font_size=font_size,
        auto_font=not no_auto_font,
    ) if any([position, font_size, no_auto_font]) else None

    # Run generation
    click.echo(f"Generating image for: {text}")
    click.echo("Step 1/3: Enhancing prompt...")
    result = pipeline.generate(
        user_text=text,
        text_style=text_style,
        width=width,
        height=height,
        save_output=True,
    )

    if result.success:
        click.echo(f"\n✅ Generation completed!")
        click.echo(f"Original text: {result.original_text}")
        click.echo(f"Enhanced prompt: {result.enhanced_prompt}")
        click.echo(f"Output saved to: {result.image_path}")
    else:
        click.echo(f"\n❌ Generation failed: {result.error_message}")
        exit(1)


if __name__ == "__main__":
    main()
