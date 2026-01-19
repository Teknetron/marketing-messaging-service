from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.marketing_messaging_service.infrastructure.database import Base


class SendRequest(Base):
    __tablename__ = "send_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    event_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # Timestamp of the event that led to this send decision.
    # Nullable for backward compatibility / ad-hoc inserts in tests.
    event_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    template_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    decided_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
