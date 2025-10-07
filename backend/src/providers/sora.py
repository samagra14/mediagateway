"""OpenAI Sora provider implementation.

Official API Documentation: https://platform.openai.com/docs/api-reference/videos
"""
import httpx
import asyncio
from typing import Optional
from .base import VideoProvider, VideoRequest, VideoResponse, ProviderFeatures


class SoraProvider(VideoProvider):
    """OpenAI Sora video generation provider.

    Implements the official OpenAI Videos API endpoints:
    - POST /v1/videos - Create video
    - GET /v1/videos/{video_id} - Retrieve video status
    - GET /v1/videos/{video_id}/content - Download video content
    """

    BASE_URL = "https://api.openai.com/v1"

    @property
    def name(self) -> str:
        return "openai"

    @property
    def models(self) -> list[str]:
        return ["sora-2", "sora-1"]

    async def validate_key(self) -> bool:
        """Validate OpenAI API key using the models endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """Generate video using Sora.

        Official endpoint: POST https://api.openai.com/v1/videos

        Request format:
        {
            "prompt": "Text description",
            "model": "sora-2",
            "seconds": "5",
            "size": "1280x720"
        }

        Response format:
        {
            "id": "video_123",
            "object": "video",
            "model": "sora-2",
            "status": "queued",
            "progress": 0,
            "created_at": 1712697600,
            "size": "1024x1808",
            "seconds": "8",
            "quality": "standard"
        }
        """
        try:
            # Prepare request according to OpenAI API spec
            payload = {
                "prompt": request.prompt,
                "model": request.model if hasattr(request, 'model') else "sora-2",
            }

            # Duration (seconds as string)
            if request.duration:
                payload["seconds"] = str(request.duration)

            # Size (resolution as "widthxheight")
            if request.aspect_ratio:
                size_map = {
                    "9:16": "720x1280",   # Portrait
                    "16:9": "1280x720",   # Landscape
                    "1:1": "1024x1024",   # Square
                }
                payload["size"] = size_map.get(request.aspect_ratio, "1280x720")

            # Make request to OpenAI Videos API
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/videos",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                # Return job ID for polling
                # OpenAI returns: {"id": "video_123", "status": "queued", ...}
                return VideoResponse(
                    job_id=data.get("id"),
                    status="processing",  # Map "queued" to our "processing" status
                    metadata=data,
                )

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", error_detail)
            except:
                pass

            return VideoResponse(
                job_id="",
                status="failed",
                error=f"HTTP {e.response.status_code}: {error_detail}",
            )
        except Exception as e:
            return VideoResponse(
                job_id="",
                status="failed",
                error=str(e),
            )

    async def check_status(self, job_id: str) -> VideoResponse:
        """Check Sora generation status.

        Official endpoint: GET https://api.openai.com/v1/videos/{video_id}

        Response format:
        {
            "id": "video_123",
            "object": "video",
            "model": "sora-2",
            "status": "completed",  // or "queued", "processing", "failed"
            "progress": 100,
            "created_at": 1712697600,
            "completed_at": 1712697700,
            "size": "1280x720",
            "seconds": "5"
        }

        When completed, download URL is at: /v1/videos/{video_id}/content
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/videos/{job_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                data = response.json()

                # Get status from response
                status = data.get("status", "processing")
                video_url = None

                # Map OpenAI status to our standard status
                status_map = {
                    "queued": "processing",
                    "processing": "processing",
                    "completed": "completed",
                    "failed": "failed",
                    "cancelled": "failed",
                }
                mapped_status = status_map.get(status, status)

                # If completed, construct the download URL
                if mapped_status == "completed":
                    # OpenAI video content is available at /v1/videos/{video_id}/content
                    video_url = f"{self.BASE_URL}/videos/{job_id}/content"

                return VideoResponse(
                    job_id=job_id,
                    status=mapped_status,
                    video_url=video_url,
                    metadata=data,
                )

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", error_detail)
            except:
                pass

            return VideoResponse(
                job_id=job_id,
                status="failed",
                error=f"HTTP {e.response.status_code}: {error_detail}",
            )
        except Exception as e:
            return VideoResponse(
                job_id=job_id,
                status="failed",
                error=str(e),
            )

    def get_supported_features(self) -> ProviderFeatures:
        """Get Sora 2 supported features.

        Based on official OpenAI documentation:
        - Supports text-to-video and image-to-video
        - Generates video with synced audio
        - Portrait: 720x1280, Landscape: 1280x720
        - Pricing: $0.10 per second
        - Default: 4 seconds, up to 20 seconds
        """
        return ProviderFeatures(
            supports_duration=True,
            supports_aspect_ratio=True,
            supports_seed=False,  # Not in current API docs
            supports_fps=False,
            supports_image_to_video=True,  # Via input_reference parameter
            supports_video_to_video=True,  # Via remix endpoint
            max_duration=20,
            available_aspect_ratios=["16:9", "9:16", "1:1"],
        )
