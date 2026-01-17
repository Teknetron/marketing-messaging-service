from datetime import datetime
from pydantic import BaseModel


class EventPropertiesIn(BaseModel):
    amount: float | None = None
    attempt_number: int | None = None
    failure_reason: str | None = None


class UserTraitsIn(BaseModel):
    email: str | None = None
    country: str | None = None
    marketing_opt_in: bool | None = None
    risk_segment: str | None = None


class EventIn(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: datetime
    properties: EventPropertiesIn | None = None
    user_traits: UserTraitsIn | None = None


class EventAccepted(BaseModel):
    status: str
