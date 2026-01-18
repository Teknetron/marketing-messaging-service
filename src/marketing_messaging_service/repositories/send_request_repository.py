from sqlalchemy.orm import Session
from sqlalchemy import func, select

from src.marketing_messaging_service.models.send_request import SendRequest
from src.marketing_messaging_service.repositories.interfaces import ISendRequestRepository


class SendRequestRepository(ISendRequestRepository):
    def add(self, db: Session, send_request: SendRequest) -> SendRequest:
        db.add(send_request)
        db.flush()
        db.refresh(send_request)
        return send_request

    def exists_for_user_and_template(self, db: Session, user_id: str, template_name: str) -> bool:
        return (
            db.query(SendRequest)
            .filter(
                SendRequest.user_id == user_id,
                SendRequest.template_name == template_name,
            )
            .first()
            is not None
        )

    def exists_for_user_and_template_on_date(self, db: Session, user_id: str, template_name: str, date) -> bool:
        return (
            db.query(SendRequest)
            .filter(
                SendRequest.user_id == user_id,
                SendRequest.template_name == template_name,
                func.date(SendRequest.decided_at) == date,
            )
            .first()
            is not None
        )

    def list_by_user(self, db: Session, user_id: str) -> list[SendRequest]:
        stmt = (
            select(SendRequest)
            .where(SendRequest.user_id == user_id)
            .order_by(SendRequest.decided_at.desc())
        )
        return list(db.scalars(stmt).all())