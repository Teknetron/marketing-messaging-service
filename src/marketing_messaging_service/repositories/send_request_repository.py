from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.send_request import SendRequest
from src.marketing_messaging_service.repositories.interfaces import \
    ISendRequestRepository


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
        ts_col = func.coalesce(SendRequest.event_timestamp, SendRequest.decided_at)
        return (
            db.query(SendRequest)
            .filter(
                SendRequest.user_id == user_id,
                SendRequest.template_name == template_name,
                func.date(ts_col) == date,
            )
            .first()
            is not None
        )

    def exists_for_user_and_template_in_day_so_far(
        self,
        db: Session,
        user_id: str,
        template_name: str,
        provided_ts: datetime,
    ) -> bool:
        # Window is strictly within the provided timestamp's calendar day:
        #   window_start < event_timestamp < provided_ts
        window_start = provided_ts.replace(hour=0, minute=0, second=0, microsecond=0)

        stmt = (
            select(SendRequest.id)
            .where(
                SendRequest.user_id == user_id,
                SendRequest.template_name == template_name,
                SendRequest.event_timestamp.is_not(None),
                SendRequest.event_timestamp >= window_start,
                SendRequest.event_timestamp <= provided_ts,
            )
            .limit(1)
        )
        return db.execute(stmt).first() is not None

    def list_by_user(self, db: Session, user_id: str) -> list[SendRequest]:
        stmt = (
            select(SendRequest)
            .where(SendRequest.user_id == user_id)
            .order_by(SendRequest.decided_at.desc())
        )
        return list(db.scalars(stmt).all())