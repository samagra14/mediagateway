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


@router.post("/v1/usage/estimate")
async def estimate_generation_cost(request: VideoGenerationRequest):
    """Estimate cost before generating a video.

    Returns cost breakdown and pricing info.
    """
    from ..services.cost_calculator import get_cost_calculator
    from ..providers import get_provider_for_model

    provider_name = request.provider or get_provider_for_model(request.model)
    cost_calc = get_cost_calculator()

    estimate = cost_calc.estimate_cost(
        provider=provider_name,
        model=request.model,
        duration_seconds=request.duration or 5,
        aspect_ratio=request.aspect_ratio or "16:9",
    )

    return {
        "model": request.model,
        "provider": provider_name,
        "duration": request.duration or 5,
        "aspect_ratio": request.aspect_ratio or "16:9",
        **estimate,
    }


@router.get("/v1/usage/detailed")
def get_detailed_usage(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get detailed usage statistics with date filtering.

    Query parameters:
    - start_date: ISO format (YYYY-MM-DD)
    - end_date: ISO format (YYYY-MM-DD)
    - provider: Filter by provider
    """
    from datetime import datetime as dt
    from sqlalchemy import func, and_

    query = db.query(Generation)

    # Apply filters
    filters = []
    if start_date:
        try:
            start_dt = dt.fromisoformat(start_date)
            filters.append(Generation.created_at >= start_dt)
        except:
            pass

    if end_date:
        try:
            end_dt = dt.fromisoformat(end_date)
            filters.append(Generation.created_at <= end_dt)
        except:
            pass

    if provider:
        filters.append(Generation.provider == provider)

    if filters:
        query = query.filter(and_(*filters))

    # Get all generations
    generations = query.all()

    # Calculate totals
    total_cost = sum(g.cost or 0.0 for g in generations)
    total_duration = sum(g.duration_seconds or 0.0 for g in generations)
    total_generation_time = sum(g.generation_time or 0.0 for g in generations)

    # Group by date
    daily_stats = {}
    for gen in generations:
        date_key = gen.created_at.date().isoformat()
        if date_key not in daily_stats:
            daily_stats[date_key] = {
                "date": date_key,
                "count": 0,
                "cost": 0.0,
                "duration": 0.0,
                "success": 0,
                "failed": 0,
            }

        daily_stats[date_key]["count"] += 1
        daily_stats[date_key]["cost"] += gen.cost or 0.0
        daily_stats[date_key]["duration"] += gen.duration_seconds or 0.0

        if gen.status == GenerationStatus.COMPLETED:
            daily_stats[date_key]["success"] += 1
        elif gen.status == GenerationStatus.FAILED:
            daily_stats[date_key]["failed"] += 1

    # Group by provider
    provider_stats = {}
    for gen in generations:
        prov = gen.provider
        if prov not in provider_stats:
            provider_stats[prov] = {
                "provider": prov,
                "count": 0,
                "cost": 0.0,
                "duration": 0.0,
                "avg_cost_per_second": 0.0,
            }

        provider_stats[prov]["count"] += 1
        provider_stats[prov]["cost"] += gen.cost or 0.0
        provider_stats[prov]["duration"] += gen.duration_seconds or 0.0

    # Calculate averages
    for prov_data in provider_stats.values():
        if prov_data["duration"] > 0:
            prov_data["avg_cost_per_second"] = prov_data["cost"] / prov_data["duration"]

    return {
        "summary": {
            "total_generations": len(generations),
            "total_cost": round(total_cost, 2),
            "total_video_duration": round(total_duration, 1),
            "total_processing_time": round(total_generation_time, 1),
            "average_cost_per_generation": round(total_cost / len(generations), 4) if generations else 0,
        },
        "daily": sorted(daily_stats.values(), key=lambda x: x["date"]),
        "by_provider": list(provider_stats.values()),
        "date_range": {
            "start": start_date,
            "end": end_date,
        },
    }


@router.get("/v1/usage/pricing")
def get_pricing_info():
    """Get pricing information for all providers and models."""
    from ..services.cost_calculator import get_cost_calculator

    cost_calc = get_cost_calculator()
    pricing = cost_calc.get_pricing_info()

    # Format for frontend
    formatted = []
    for provider, models in pricing.items():
        for model, rates in models.items():
            formatted.append({
                "provider": provider,
                "model": model,
                "per_second": rates["per_second"],
                "base_cost": rates["base_cost"],
                "currency": "USD",
                "examples": {
                    "5_seconds": round(rates["per_second"] * 5, 2),
                    "10_seconds": round(rates["per_second"] * 10, 2),
                    "20_seconds": round(rates["per_second"] * 20, 2),
                },
            })

    return {
        "pricing": formatted,
        "last_updated": "2025-10-07",
        "note": "Prices are estimates. Actual costs may vary.",
    }


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
                        # Parse size from metadata (e.g., "1280x720")
                        size = status.metadata.get("size", "1280x720")
                        if "x" in str(size):
                            try:
                                width, height = map(int, str(size).split("x"))
                                generation.width = width
                                generation.height = height
                            except:
                                generation.width = 1920
                                generation.height = 1080
                        else:
                            generation.width = 1920
                            generation.height = 1080

                        # Get duration from metadata or use requested duration
                        duration_str = status.metadata.get("seconds", str(request.duration))
                        try:
                            generation.duration_seconds = float(duration_str)
                        except:
                            generation.duration_seconds = request.duration

                    # Calculate cost using the cost calculator
                    from ..services.cost_calculator import get_cost_calculator
                    cost_calc = get_cost_calculator()

                    resolution = f"{generation.width}x{generation.height}" if generation.width else None
                    calculated_cost = cost_calc.calculate_cost(
                        provider=provider_name,
                        model=request.model,
                        duration_seconds=generation.duration_seconds or request.duration,
                        resolution=resolution
                    )
                    generation.cost = calculated_cost

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
