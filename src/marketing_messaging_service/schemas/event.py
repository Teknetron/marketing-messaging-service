from datetime import datetime
from pydantic import BaseModel


class UserTraitsIn(BaseModel):
    email: str | None = None
    country: str | None = None
    marketing_opt_in: bool | None = None
    risk_segment: str | None = None


class EventIn(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: datetime
    properties: dict | None = None
    user_traits: UserTraitsIn | None = None


class EventProcessingResult(BaseModel):
    event_id: int
    user_id: str
    event_type: str

    matched_rule: str | None = None
    action_type: str | None = None
    template_name: str | None = None
    channel: str | None = None

    outcome: str  # allow | suppress | alert | none
    reason: str | None = None


# Keeping the old schema in case something else still imports it.
class EventAccepted(BaseModel):
    status: str
