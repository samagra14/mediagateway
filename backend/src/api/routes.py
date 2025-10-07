"""API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

from ..db.database import get_db
from ..models import Generation, GenerationStatus, APIKey, KeyStatus
from ..services.key_manager import get_key_manager
from ..services.video_storage import get_video_storage
from ..providers import create_provider, get_provider_for_model, PROVIDERS, VideoRequest
from .schemas import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    APIKeyRequest,
    APIKeyResponse,
    ProviderInfo,
    UsageStatsResponse,
)

router = APIRouter()


# Video Generation Routes
@router.post("/v1/video/generations", response_model=VideoGenerationResponse)
async def create_video_generation(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Create a new video generation."""
    # Determine provider
    provider_name = request.provider or get_provider_for_model(request.model)

    # Get API key
    key_manager = get_key_manager()
    api_key = key_manager.get_key_by_provider(db, provider_name)

    if not api_key or api_key.status != KeyStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"No active API key found for provider: {provider_name}",
        )

    # Create generation record
    generation_id = f"gen_{uuid.uuid4().hex[:12]}"
    generation = Generation(
        id=generation_id,
        provider=provider_name,
        model=request.model,
        prompt=request.prompt,
        parameters={
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio,
            "seed": request.seed,
            "fps": request.fps,
        },
        status=GenerationStatus.QUEUED,
    )

    db.add(generation)
    db.commit()
    db.refresh(generation)

    # Start background task to generate video
    background_tasks.add_task(
        process_video_generation,
        generation_id,
        provider_name,
        key_manager.decrypt_key(api_key),
        request,
    )

    return VideoGenerationResponse(**generation.to_dict())


@router.get("/v1/video/generations/{generation_id}", response_model=VideoGenerationResponse)
def get_video_generation(
    generation_id: str,
    db: Session = Depends(get_db),
):
    """Get video generation status."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()

    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")

    return VideoGenerationResponse(**generation.to_dict())


@router.get("/v1/video/generations", response_model=List[VideoGenerationResponse])
def list_video_generations(
    skip: int = 0,
    limit: int = 50,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List video generations."""
    query = db.query(Generation)

    if provider:
        query = query.filter(Generation.provider == provider)
    if status:
        query = query.filter(Generation.status == status)

    generations = query.order_by(Generation.created_at.desc()).offset(skip).limit(limit).all()

    return [VideoGenerationResponse(**g.to_dict()) for g in generations]


@router.delete("/v1/video/generations/{generation_id}")
def delete_video_generation(
    generation_id: str,
    db: Session = Depends(get_db),
):
    """Delete a video generation."""
    generation = db.query(Generation).filter(Generation.id == generation_id).first()

    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")

    # Delete video file
    if generation.video_path:
        storage = get_video_storage()
        filename = generation.video_path.split("/")[-1]
        storage.delete_video(filename)

    # Delete record
    db.delete(generation)
    db.commit()

    return {"message": "Generation deleted successfully"}


# API Key Routes
@router.post("/v1/keys", response_model=APIKeyResponse)
async def add_api_key(
    request: APIKeyRequest,
    db: Session = Depends(get_db),
):
    """Add a new API key."""
    if request.provider not in PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {request.provider}",
        )

    # Validate key
    try:
        provider = create_provider(request.provider, request.api_key)
        is_valid = await provider.validate_key()

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid API key",
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to validate key: {str(e)}",
        )

    # Store key
    key_manager = get_key_manager()
    api_key = key_manager.add_key(db, request.provider, request.api_key)
    api_key.last_validated = datetime.utcnow()
    db.commit()

    return APIKeyResponse(**api_key.to_dict(include_key=True))


@router.get("/v1/keys", response_model=List[APIKeyResponse])
def list_api_keys(db: Session = Depends(get_db)):
    """List all API keys."""
    key_manager = get_key_manager()
    keys = key_manager.list_keys(db)
    return [APIKeyResponse(**k.to_dict(include_key=True)) for k in keys]


@router.delete("/v1/keys/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
):
    """Delete an API key."""
    key_manager = get_key_manager()
    success = key_manager.delete_key(db, key_id)

    if not success:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"message": "Key deleted successfully"}


@router.post("/v1/keys/{key_id}/validate")
async def validate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
):
    """Validate an API key."""
    key_manager = get_key_manager()
    api_key = key_manager.get_key(db, key_id)

    if not api_key:
        raise HTTPException(status_code=404, detail="Key not found")

    try:
        provider = create_provider(api_key.provider, key_manager.decrypt_key(api_key))
        is_valid = await provider.validate_key()

        status = KeyStatus.ACTIVE if is_valid else KeyStatus.INVALID
        key_manager.update_key_status(db, key_id, status)

        return {"valid": is_valid, "status": status.value}
    except Exception as e:
        key_manager.update_key_status(db, key_id, KeyStatus.INVALID)
        return {"valid": False, "status": "invalid", "error": str(e)}


# Provider Routes
@router.get("/v1/providers", response_model=List[ProviderInfo])
def list_providers(db: Session = Depends(get_db)):
    """List all available providers."""
    key_manager = get_key_manager()
    provider_keys = {k.provider: k for k in key_manager.list_keys(db)}

    provider_info = []
    for name, provider_class in PROVIDERS.items():
        # Create temporary instance to get features
        temp_provider = provider_class(api_key="dummy")
        features = temp_provider.get_supported_features()

        api_key = provider_keys.get(name)

        info = ProviderInfo(
            name=name,
            display_name=name.title(),
            models=temp_provider.models,
            features=features.dict(),
            has_key=api_key is not None,
            key_status=api_key.status.value if api_key else None,
        )
        provider_info.append(info)

    return provider_info


# Usage Statistics Routes
@router.get("/v1/usage/stats", response_model=UsageStatsResponse)
def get_usage_stats(db: Session = Depends(get_db)):
    """Get usage statistics."""
    from sqlalchemy import func

    # Total stats
    total_generations = db.query(func.count(Generation.id)).scalar() or 0
    total_cost = db.query(func.sum(Generation.cost)).scalar() or 0.0
    total_success = (
        db.query(func.count(Generation.id))
        .filter(Generation.status == GenerationStatus.COMPLETED)
        .scalar()
        or 0
    )
    total_failure = (
        db.query(func.count(Generation.id))
        .filter(Generation.status == GenerationStatus.FAILED)
        .scalar()
        or 0
    )

    # By provider
    by_provider = (
        db.query(
            Generation.provider,
            func.count(Generation.id).label("count"),
            func.sum(Generation.cost).label("total_cost"),
            func.avg(Generation.generation_time).label("avg_time"),
        )
        .group_by(Generation.provider)
        .all()
    )

    # By model
    by_model = (
        db.query(
            Generation.model,
            func.count(Generation.id).label("count"),
            func.sum(Generation.cost).label("total_cost"),
            func.avg(Generation.generation_time).label("avg_time"),
        )
        .group_by(Generation.model)
        .all()
    )

    # Recent generations
    recent = (
        db.query(Generation)
        .order_by(Generation.created_at.desc())
        .limit(10)
        .all()
    )

    return UsageStatsResponse(
        total_generations=total_generations,
        total_cost=total_cost,
        total_success=total_success,
        total_failure=total_failure,
        success_rate=total_success / total_generations if total_generations > 0 else 0,
        by_provider=[
            {
                "provider": p.provider,
                "count": p.count,
                "total_cost": p.total_cost or 0.0,
                "avg_time": p.avg_time or 0.0,
            }
            for p in by_provider
        ],
        by_model=[
            {
                "model": m.model,
                "count": m.count,
                "total_cost": m.total_cost or 0.0,
                "avg_time": m.avg_time or 0.0,
            }
            for m in by_model
        ],
        recent_generations=[VideoGenerationResponse(**g.to_dict()) for g in recent],
    )


# Background task for video generation
async def process_video_generation(
    generation_id: str,
    provider_name: str,
    api_key: str,
    request: VideoGenerationRequest,
):
    """Process video generation in background."""
    from ..db.database import SessionLocal

    db = SessionLocal()
    try:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if not generation:
            return

        # Update status to processing
        generation.status = GenerationStatus.PROCESSING
        db.commit()

        # Create provider
        provider = create_provider(provider_name, api_key)

        # Generate video
        video_request = VideoRequest(
            prompt=request.prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio,
            seed=request.seed,
            fps=request.fps,
        )

        start_time = datetime.utcnow()
        result = await provider.generate_video(video_request)

        if result.status == "failed":
            generation.status = GenerationStatus.FAILED
            generation.error_message = result.error
            db.commit()
            return

        # Poll for completion
        max_attempts = 60  # 5 minutes with 5-second intervals
        for _ in range(max_attempts):
            await asyncio.sleep(5)
            status = await provider.check_status(result.job_id)

            if status.status == "completed":
                # Download video
                if status.video_url:
                    storage = get_video_storage()
                    filename = f"{generation_id}.mp4"

                    # For OpenAI, we need to pass the Authorization header
                    headers = None
                    if provider_name == "openai":
                        headers = {"Authorization": f"Bearer {api_key}"}

                    video_path = await storage.download_video(
                        status.video_url,
                        filename,
                        headers=headers
                    )

                    # Update generation
                    end_time = datetime.utcnow()
                    generation.status = GenerationStatus.COMPLETED
                    generation.video_url = f"http://localhost:3001{video_path}"
                    generation.video_path = video_path
                    generation.generation_time = (end_time - start_time).total_seconds()
                    generation.completed_at = end_time

                    # Extract metadata if available
                    if status.metadata:
                        generation.width = status.metadata.get("width", 1920)
                        generation.height = status.metadata.get("height", 1080)
                        generation.duration_seconds = status.metadata.get("duration", request.duration)
                        generation.cost = status.metadata.get("cost", 0.0)

                    db.commit()
                break

            elif status.status == "failed":
                generation.status = GenerationStatus.FAILED
                generation.error_message = status.error
                db.commit()
                break

        else:
            # Timeout
            generation.status = GenerationStatus.FAILED
            generation.error_message = "Generation timeout"
            db.commit()

    except Exception as e:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if generation:
            generation.status = GenerationStatus.FAILED
            generation.error_message = str(e)
            db.commit()
    finally:
        db.close()
