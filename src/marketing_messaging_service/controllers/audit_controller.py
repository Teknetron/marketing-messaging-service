from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.marketing_messaging_service.infrastructure.database import create_session
from src.marketing_messaging_service.schemas.audit import AuditResponse


router = APIRouter(prefix="/audit", tags=["audit"])


def get_db():
    with create_session() as session:
        yield session


@router.get("/{user_id}", response_model=AuditResponse)
def get_audit(user_id: str, db: Session = Depends(get_db)):
    # Service interaction will be added later
    return AuditResponse(
        user_id=user_id,
        events=[],
        send_requests=[],
        suppressions=[],
    )
