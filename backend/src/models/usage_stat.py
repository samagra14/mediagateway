"""Usage Statistics model."""
from sqlalchemy import Column, Integer, String, Float, Date
from datetime import date
from ..db.database import Base


class UsageStat(Base):
    """Usage statistics tracking."""

    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    count = Column(Integer, default=0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    avg_time = Column(Float, default=0.0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    date = Column(Date, default=date.today, nullable=False, index=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "count": self.count,
            "total_cost": self.total_cost,
            "avg_time": self.avg_time,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_count / self.count if self.count > 0 else 0,
            "date": self.date.isoformat(),
        }
