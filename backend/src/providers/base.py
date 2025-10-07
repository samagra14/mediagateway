"""Base provider interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class VideoRequest(BaseModel):
    """Standard video generation request."""

    prompt: str
    duration: Optional[int] = 5
    aspect_ratio: Optional[str] = "16:9"
    seed: Optional[int] = None
    fps: Optional[int] = None
    resolution: Optional[str] = None


class VideoResponse(BaseModel):
    """Standard video generation response."""

    job_id: str
    status: str  # queued, processing, completed, failed
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProviderFeatures(BaseModel):
    """Provider supported features."""

    supports_duration: bool = True
    supports_aspect_ratio: bool = True
    supports_seed: bool = True
    supports_fps: bool = False
    supports_image_to_video: bool = False
    supports_video_to_video: bool = False
    max_duration: int = 10
    available_aspect_ratios: list[str] = ["16:9", "9:16", "1:1"]


class VideoProvider(ABC):
    """Base class for video generation providers."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def models(self) -> list[str]:
        """List of available models."""
        pass

    @abstractmethod
    async def validate_key(self) -> bool:
        """Validate API key.

        Returns:
            True if key is valid, False otherwise
        """
        pass

    @abstractmethod
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Generate video from prompt.

        Args:
            request: Video generation request

        Returns:
            Video response with job ID
        """
        pass

    @abstractmethod
    async def check_status(self, job_id: str) -> VideoResponse:
        """Check generation status.

        Args:
            job_id: Job ID from initial request

        Returns:
            Current status and video URL if completed
        """
        pass

    @abstractmethod
    def get_supported_features(self) -> ProviderFeatures:
        """Get supported features.

        Returns:
            Provider features
        """
        pass

    def _normalize_aspect_ratio(self, aspect_ratio: str) -> tuple[int, int]:
        """Convert aspect ratio string to width/height tuple."""
        ratios = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1080, 1080),
            "4:3": (1440, 1080),
            "21:9": (2560, 1080),
        }
        return ratios.get(aspect_ratio, (1920, 1080))
