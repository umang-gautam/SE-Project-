from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PerformanceRecord(Base):
    """Links to Topic, not Assignment: mastery is tracked per concept."""

    __tablename__ = "performance_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"))
    score: Mapped[float] = mapped_column(Float)  # 0..100
    record_type: Mapped[str] = mapped_column(String(20), default="self_assessed")  # self_assessed | quiz | exam
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
