from sqlalchemy.orm import Session

from src.marketing_messaging_service.db_debug import print_db_connection_info
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
