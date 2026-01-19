from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.repositories.interfaces import IEventRepository


class EventRepository(IEventRepository):
    def add(self, db: Session, event: Event) -> Event:
        db.add(event)
        db.flush()
        db.refresh(event)
        return event

    def get_by_id(self, db: Session, event_id: int) -> Event | None:
        return (
            db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )

    def get_latest_by_user_and_type(self, db: Session, user_id: str, event_type: str) -> Event | None:
        return (
            db.query(Event)
            .filter(Event.user_id == user_id, Event.event_type == event_type)
            .order_by(Event.event_timestamp.desc())
            .first()
        )

    def list_by_user(self, db: Session, user_id: str) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.user_id == user_id)
            .order_by(Event.event_timestamp.desc())
        )
        return list(db.scalars(stmt).all())

    def exists_by_user_and_type_in_window(
        self,
        db: Session,
        user_id: str,
        event_type: str,
        window_start: datetime,
        window_end: datetime,
    ) -> bool:
        # TODO: this is not neceserally repository, since we have some logic here
        found = (
            db.query(Event.id)
            .filter(
                Event.user_id == user_id,
                Event.event_type == event_type,
                Event.event_timestamp >= window_start,
                Event.event_timestamp <= window_end,
            )
            .first()
        )
        return found is not None
