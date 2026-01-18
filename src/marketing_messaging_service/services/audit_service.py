from sqlalchemy.orm import Session

from src.marketing_messaging_service.repositories.event_repository import EventRepository
from src.marketing_messaging_service.repositories.send_request_repository import SendRequestRepository
from src.marketing_messaging_service.repositories.suppression_repository import SuppressionRepository
from src.marketing_messaging_service.schemas.audit import AuditLog, AuditLogItem


class AuditService:
    def __init__(
        self,
        event_repository: EventRepository,
        send_request_repository: SendRequestRepository,
        suppression_repository: SuppressionRepository,
    ):
        self.event_repository = event_repository
        self.send_request_repository = send_request_repository
        self.suppression_repository = suppression_repository

    def get_audit_log(self, db: Session, user_id: str) -> AuditLog:
        events = self.event_repository.list_by_user(db, user_id)
        send_requests = self.send_request_repository.list_by_user(db, user_id)
        suppressions = self.suppression_repository.list_by_user(db, user_id)

        items: list[AuditLogItem] = []

        for e in events:
            items.append(
                AuditLogItem(
                    timestamp=e.event_timestamp,
                    kind="event",
                    event_id=e.id,
                    event_type=e.event_type,
                )
            )

        for s in send_requests:
            # Simple inference: internal channel is "alert", everything else is "allow"
            outcome = "alert" if s.channel == "internal" else "allow"

            items.append(
                AuditLogItem(
                    timestamp=s.decided_at,
                    kind="send_request",
                    template_name=s.template_name,
                    channel=s.channel,
                    outcome=outcome,
                    reason=s.reason,
                )
            )

        for sup in suppressions:
            items.append(
                AuditLogItem(
                    timestamp=sup.decided_at,
                    kind="suppression",
                    event_id=sup.event_id,
                    template_name=sup.template_name,
                    outcome="suppress",
                    reason=sup.suppression_reason,
                )
            )

        items.sort(key=lambda x: x.timestamp, reverse=True)

        return AuditLog(user_id=user_id, items=items)
