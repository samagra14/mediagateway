"""Video storage service."""
import os
import aiofiles
import httpx
from pathlib import Path
from typing import Optional
from ..config import get_settings
import uuid


class VideoStorage:
    """Handles video file storage."""

    def __init__(self):
        self.settings = get_settings()
        self.storage_path = Path(self.settings.storage_path)
        self.temp_path = Path(self.settings.temp_path)

        # Ensure directories exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)

    async def download_video(
        self,
        url: str,
        filename: Optional[str] = None,
        headers: Optional[dict] = None
    ) -> str:
        """Download video from URL and save to storage.

        Args:
            url: URL to download from
            filename: Optional filename (auto-generated if not provided)
            headers: Optional HTTP headers (for authenticated downloads like OpenAI)

        Returns:
            Relative path to saved video
        """
        if filename is None:
            filename = f"{uuid.uuid4()}.mp4"

        file_path = self.storage_path / filename

        async with httpx.AsyncClient(timeout=300.0) as client:
            # Add headers if provided (e.g., Authorization for OpenAI)
            request_headers = headers or {}

            async with client.stream("GET", url, headers=request_headers) as response:
                response.raise_for_status()
                async with aiofiles.open(file_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        await f.write(chunk)

        return f"/videos/{filename}"

    def get_video_path(self, filename: str) -> Path:
        """Get full path to video file."""
        return self.storage_path / filename

    def delete_video(self, filename: str) -> bool:
        """Delete a video file."""
        file_path = self.storage_path / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def video_exists(self, filename: str) -> bool:
        """Check if video file exists."""
        return (self.storage_path / filename).exists()


# Singleton instance
_video_storage = None


def get_video_storage() -> VideoStorage:
    """Get video storage instance."""
    global _video_storage
    if _video_storage is None:
        _video_storage = VideoStorage()
    return _video_storage
