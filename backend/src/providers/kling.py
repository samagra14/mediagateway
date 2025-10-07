"""Kling AI provider implementation."""
import httpx
from typing import Optional
from .base import VideoProvider, VideoRequest, VideoResponse, ProviderFeatures


class KlingProvider(VideoProvider):
    """Kling AI video generation provider."""

    BASE_URL = "https://api.klingai.com/v1"

    @property
    def name(self) -> str:
        return "kling"

    @property
    def models(self) -> list[str]:
        return ["kling-1.5", "kling-1.0"]

    async def validate_key(self) -> bool:
        """Validate Kling API key."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/account",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Generate video using Kling."""
        try:
            payload = {
                "prompt": request.prompt,
                "model": "kling-v1.5",
            }

            if request.duration:
                payload["duration"] = request.duration
            if request.aspect_ratio:
                payload["aspect_ratio"] = request.aspect_ratio
            if request.seed:
                payload["seed"] = request.seed

            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/videos/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return VideoResponse(
                    job_id=data.get("task_id", data.get("id")),
                    status="processing",
                    metadata=data,
                )

        except httpx.HTTPStatusError as e:
            return VideoResponse(
                job_id="",
                status="failed",
                error=f"HTTP {e.response.status_code}: {e.response.text}",
            )
        except Exception as e:
            return VideoResponse(
                job_id="",
                status="failed",
                error=str(e),
            )

    async def check_status(self, job_id: str) -> VideoResponse:
        """Check Kling generation status."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/videos/generations/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                data = response.json()

                status_map = {
                    "pending": "processing",
                    "running": "processing",
                    "success": "completed",
                    "failed": "failed",
                }

                status = status_map.get(data.get("task_status"), "processing")
                video_url = data.get("task_result", {}).get("video_url") if status == "completed" else None

                return VideoResponse(
                    job_id=job_id,
                    status=status,
                    video_url=video_url,
                    metadata=data,
                )

        except httpx.HTTPStatusError as e:
            return VideoResponse(
                job_id=job_id,
                status="failed",
                error=f"HTTP {e.response.status_code}: {e.response.text}",
            )
        except Exception as e:
            return VideoResponse(
                job_id=job_id,
                status="failed",
                error=str(e),
            )

    def get_supported_features(self) -> ProviderFeatures:
        """Get Kling supported features."""
        return ProviderFeatures(
            supports_duration=True,
            supports_aspect_ratio=True,
            supports_seed=True,
            supports_fps=True,
            supports_image_to_video=True,
            supports_video_to_video=True,
            max_duration=10,
            available_aspect_ratios=["16:9", "9:16", "1:1"],
        )
