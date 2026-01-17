from datetime import datetime
from pydantic import BaseModel


class AuditEvent(BaseModel):
    id: int
    event_type: str
    event_timestamp: datetime


class AuditSend(BaseModel):
    id: int
    template_name: str
    channel: str
    decided_at: datetime


class AuditSuppression(BaseModel):
    id: int
    template_name: str
    suppression_reason: str
    decided_at: datetime


class AuditResponse(BaseModel):
    user_id: str
    events: list[AuditEvent]
    send_requests: list[AuditSend]
    suppressions: list[AuditSuppression]
