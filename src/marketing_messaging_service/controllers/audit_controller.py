from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.marketing_messaging_service.infrastructure.database import create_session
from src.marketing_messaging_service.repositories import EventRepository, SendRequestRepository, SuppressionRepository
from src.marketing_messaging_service.schemas.audit import AuditLog
from src.marketing_messaging_service.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])

event_repository = EventRepository()
send_request_repository = SendRequestRepository()
suppression_repository = SuppressionRepository()

audit_service = AuditService(
    event_repository=event_repository,
    send_request_repository=send_request_repository,
    suppression_repository=suppression_repository,
)


def get_db():
    with create_session() as session:
        yield session


@router.get("/{user_id}", response_model=AuditLog)
def get_audit(user_id: str, db: Session = Depends(get_db)):
    return audit_service.get_audit_log(db=db, user_id=user_id)
