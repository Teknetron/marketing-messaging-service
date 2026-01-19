from sqlalchemy.orm import Session

from src.marketing_messaging_service.repositories.decision_repository import DecisionRepository
from src.marketing_messaging_service.schemas.audit import AuditLog, AuditLogItem


class AuditService:
    def __init__(self, decision_repository: DecisionRepository):
        self.decision_repository = decision_repository

    def get_audit_log(self, db: Session, user_id: str) -> AuditLog:
        decisions = self.decision_repository.list_by_user(db, user_id)

        items: list[AuditLogItem] = []
        for d in decisions:
            items.append(
                AuditLogItem(
                    timestamp=d.created_at,
                    kind="decision",
                    event_id=d.event_id,
                    user_id=d.user_id,
                    event_type=d.event_type,
                    matched_rule=d.matched_rule,
                    action_type=d.action_type,
                    outcome=d.outcome,
                    reason=d.reason,
                    template_name=d.template_name,
                    channel=d.channel,
                )
            )

        items.sort(key=lambda x: x.timestamp, reverse=True)
        return AuditLog(user_id=user_id, items=items)
