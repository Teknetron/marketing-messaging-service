from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.send_request import SendRequest


class SendRequestRepository:
    def add(self, db: Session, send_request: SendRequest) -> SendRequest:
        db.add(send_request)
        db.flush()
        db.refresh(send_request)
        return send_request
