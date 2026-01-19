from datetime import datetime
from pydantic import BaseModel


class AuditLogItem(BaseModel):
    timestamp: datetime
    kind: str  # "decision"

    event_id: int | None = None
    user_id: str | None = None
    event_type: str | None = None

    matched_rule: str | None = None

    action_type: str | None = None
    outcome: str | None = None
    reason: str | None = None

    template_name: str | None = None
    channel: str | None = None


class AuditLog(BaseModel):
    user_id: str
    items: list[AuditLogItem]
