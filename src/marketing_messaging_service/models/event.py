from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.marketing_messaging_service.infrastructure.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    properties = relationship(
        "EventProperties",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )

    user_traits = relationship(
        "UserTraits",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
