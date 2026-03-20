from sqlalchemy import String, Text, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class FlowEvent(Base):
    __tablename__ = "flow_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    outcome_id: Mapped[int] = mapped_column(Integer, ForeignKey("outcomes.id"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False
    )
