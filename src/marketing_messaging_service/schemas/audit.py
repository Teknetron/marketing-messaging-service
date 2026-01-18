from datetime import datetime
from pydantic import BaseModel


class AuditLogItem(BaseModel):
    timestamp: datetime
    kind: str

    event_id: int | None = None
    event_type: str | None = None

    template_name: str | None = None
    channel: str | None = None

    outcome: str | None = None  # allow | alert | suppress
    reason: str | None = None


class AuditLog(BaseModel):
    user_id: str
    items: list[AuditLogItem]
