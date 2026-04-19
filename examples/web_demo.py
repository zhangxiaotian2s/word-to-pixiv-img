"""
Simple FastAPI web demo for Word-to-Pixiv Anime Background Generator.

Run with:
    uvicorn examples.web_demo:app --reload --port 8000

Then visit:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path

from src.config.settings import settings
from src.core.pipeline import AnimeBackgroundPipeline
from src.models.types import GenerationResult, TextStyle


app = FastAPI(
    title="Word-to-Pixiv Anime Background Generator",
    description="Convert text to beautiful anime background image with text overlay",
    version="0.1.0",
)

# Add CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (lazy initialization)
pipeline: Optional[AnimeBackgroundPipeline] = None


def get_pipeline() -> AnimeBackgroundPipeline:
    """Get or create pipeline instance."""
    global pipeline
    if pipeline is None:
        pipeline = AnimeBackgroundPipeline()
    return pipeline


class GenerateRequest(BaseModel):
    """Generate request body."""
    text: str = Field(..., description="Text to convert to image", min_length=1, max_length=500)
    position: Optional[str] = Field(
        None,
        description="Text position: bottom, top, center, auto",
        pattern="^(bottom|top|center|auto)$",
    )
    width: Optional[int] = Field(None, description="Image width", ge=512, le=2560)
    height: Optional[int] = Field(None, description="Image height", ge=512, le=2560)
    font_size: Optional[int] = Field(None, description="Font size", ge=12, le=120)
    auto_font: Optional[bool] = Field(True, description="Auto select font based on text mood")


@app.get("/")
async def root():
    return {
        "message": "Word-to-Pixiv Anime Background Generator API",
        "docs": "/docs",
        "usage": "POST /generate to get image",
    }


@app.post("/generate")
async def generate(request: GenerateRequest):
    """Generate anime background image from text."""
    pipe = get_pipeline()

    # Build text style
    text_style = TextStyle()
    if request.position:
        text_style.position = request.position
    if request.font_size:
        text_style.font_size = request.font_size
    if request.auto_font is not None:
        text_style.auto_font = request.auto_font

    result = pipe.generate(
        user_text=request.text,
        text_style=text_style if any([request.position, request.font_size, request.auto_font is not None]) else None,
        width=request.width,
        height=request.height,
        save_output=True,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error_message)

    if not result.image_path or not result.image_path.exists():
        raise HTTPException(status_code=500, detail="Image not saved")

    return FileResponse(
        result.image_path,
        media_type="image/png",
        filename=result.image_path.name,
    )


@app.get("/outputs/{filename}")
async def get_output(filename: str):
    """Get a previously generated output image."""
    output_dir = Path(settings.output_dir)
    file_path = output_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path, media_type="image/png")
