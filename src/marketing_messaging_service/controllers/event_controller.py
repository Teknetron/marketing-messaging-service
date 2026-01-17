from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.marketing_messaging_service.infrastructure.database import create_session
from src.marketing_messaging_service.schemas.event import EventIn, EventAccepted


router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    with create_session() as session:
        yield session


@router.post("/", response_model=EventAccepted)
def ingest_event(payload: EventIn, db: Session = Depends(get_db)):
    # Actual service call will be added in the next step
    return EventAccepted(status="accepted")
