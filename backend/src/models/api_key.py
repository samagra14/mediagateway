"""API Key model."""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
import enum
from ..db.database import Base


class KeyStatus(str, enum.Enum):
    """API Key status enum."""

    ACTIVE = "active"
    INVALID = "invalid"
    QUOTA_EXCEEDED = "quota_exceeded"
    REVOKED = "revoked"


class APIKey(Base):
    """API Key model for storing provider credentials."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)
    encrypted_key = Column(String, nullable=False)
    status = Column(SQLEnum(KeyStatus), default=KeyStatus.ACTIVE, nullable=False)
    last_validated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self, include_key: bool = False):
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "provider": self.provider,
            "status": self.status.value,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "created_at": self.created_at.isoformat(),
        }
        if include_key:
            data["key_preview"] = f"{self.encrypted_key[:8]}...{self.encrypted_key[-4:]}"
        return data
