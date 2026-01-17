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


class EventAccepted(BaseModel):
    status: str
