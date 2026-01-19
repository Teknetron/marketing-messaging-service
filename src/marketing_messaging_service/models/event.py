from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.marketing_messaging_service.infrastructure.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Dynamic event payload stored as JSON.
    properties: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    user_traits = relationship(
        "UserTraits",
        back_populates="event",
        cascade="all, delete-orphan",
        uselist=False,
    )
