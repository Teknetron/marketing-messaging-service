from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.marketing_messaging_service.infrastructure.database import Base


class EventProperties(Base):
    __tablename__ = "event_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        unique=True,
    )

    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    attempt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)

    event = relationship("Event", back_populates="properties")
