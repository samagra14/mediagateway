"""Video Generation model."""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Enum as SQLEnum
from datetime import datetime
import enum
from ..db.database import Base


class GenerationStatus(str, enum.Enum):
    """Generation status enum."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Generation(Base):
    """Video generation record."""

    __tablename__ = "generations"

    id = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    prompt = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    video_url = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.QUEUED, nullable=False)
    error_message = Column(String, nullable=True)
    cost = Column(Float, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    generation_time = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    provider_job_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "object": "video.generation",
            "created": int(self.created_at.timestamp()),
            "model": self.model,
            "provider": self.provider,
            "status": self.status.value,
            "prompt": self.prompt,
            "parameters": self.parameters,
            "video": {
                "url": self.video_url,
                "duration": self.duration_seconds,
                "width": self.width,
                "height": self.height,
            } if self.video_url else None,
            "usage": {
                "cost": self.cost,
                "time_seconds": self.generation_time,
            } if self.cost or self.generation_time else None,
            "error": self.error_message,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
