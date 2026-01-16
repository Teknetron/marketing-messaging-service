from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.marketing_messaging_service.infrastructure.database import Base


class UserTraits(Base):
    __tablename__ = "user_traits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        unique=True,
    )

    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    country: Mapped[str | None] = mapped_column(String(8), nullable=True)
    marketing_opt_in: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    risk_segment: Mapped[str | None] = mapped_column(String(32), nullable=True)

    event = relationship("Event", back_populates="user_traits")
