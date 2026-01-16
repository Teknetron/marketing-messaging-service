from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.event import Event


class EventRepository:
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
