"""API request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class VideoGenerationRequest(BaseModel):
    """Video generation request schema."""

    model: str = Field(..., description="Model name (e.g., sora-2, runway-gen3)")
    prompt: str = Field(..., description="Text prompt for video generation")
    provider: Optional[str] = Field(None, description="Provider name (auto-detected if not provided)")
    duration: Optional[int] = Field(5, description="Video duration in seconds", ge=1, le=10)
    aspect_ratio: Optional[str] = Field("16:9", description="Aspect ratio")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    fps: Optional[int] = Field(None, description="Frames per second")


class VideoObject(BaseModel):
    """Video object in response."""

    url: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


class UsageObject(BaseModel):
    """Usage information."""

    cost: Optional[float] = None
    time_seconds: Optional[float] = None


class VideoGenerationResponse(BaseModel):
    """Video generation response schema."""

    id: str
    object: str = "video.generation"
    created: int
    model: str
    provider: str
    status: str
    prompt: Optional[str] = None
    video: Optional[VideoObject] = None
    usage: Optional[UsageObject] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None


class APIKeyRequest(BaseModel):
    """API key creation request."""

    provider: str = Field(..., description="Provider name (openai, runway, kling)")
    api_key: str = Field(..., description="API key")


class APIKeyResponse(BaseModel):
    """API key response."""

    id: int
    provider: str
    status: str
    last_validated: Optional[str] = None
    created_at: str
    key_preview: Optional[str] = None


class ProviderInfo(BaseModel):
    """Provider information."""

    name: str
    display_name: str
    models: list[str]
    features: Dict[str, Any]
    has_key: bool = False
    key_status: Optional[str] = None


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""

    total_generations: int
    total_cost: float
    total_success: int
    total_failure: int
    success_rate: float
    by_provider: list[Dict[str, Any]]
    by_model: list[Dict[str, Any]]
    recent_generations: list[VideoGenerationResponse]
