from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey

from src.marketing_messaging_service.infrastructure.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(String, index=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))

    event_type: Mapped[str] = mapped_column(String)
    matched_rule: Mapped[str | None] = mapped_column(String, nullable=True)

    action_type: Mapped[str] = mapped_column(String)   # send | alert | suppress | none
    outcome: Mapped[str] = mapped_column(String)       # allow | alert | suppress | none
    reason: Mapped[str] = mapped_column(String)        # "matched rule X", "suppressed by Y"

    template_name: Mapped[str | None] = mapped_column(String, nullable=True)
    channel: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
