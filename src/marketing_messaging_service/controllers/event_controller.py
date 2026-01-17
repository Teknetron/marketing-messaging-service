from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.marketing_messaging_service.infrastructure.database import create_session
from src.marketing_messaging_service.repositories import EventRepository, SendRequestRepository, SuppressionRepository
from src.marketing_messaging_service.schemas.event import EventIn, EventAccepted
from src.marketing_messaging_service.services.event_processing_service import EventProcessingService

event_service = EventProcessingService(
    event_repository=EventRepository(),
    send_request_repository=SendRequestRepository(),
    suppression_repository=SuppressionRepository(),
)
router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    with create_session() as session:
        yield session


@router.post("/", response_model=EventAccepted)
def ingest_event(payload: EventIn, db: Session = Depends(get_db)):
    event_service.process_event(db, payload)
    return EventAccepted(status="accepted")

