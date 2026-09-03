from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Subject(Base):
    """Shared catalog. Students attach through Enrollment, not by owning rows here."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    credits: Mapped[float] = mapped_column(Float)
    weekly_effort_hours: Mapped[float] = mapped_column(Float)
