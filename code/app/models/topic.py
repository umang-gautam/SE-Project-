from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Topic(Base):
    """Hangs off Subject, not Enrollment: 'Linked Lists' is the same topic for every student."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    difficulty: Mapped[int] = mapped_column(Integer, default=2)  # 1 easy .. 3 hard
    estimated_hours: Mapped[float] = mapped_column(Float, default=2.0)
