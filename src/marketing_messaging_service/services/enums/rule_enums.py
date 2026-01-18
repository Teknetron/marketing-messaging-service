from enum import Enum


class ActionType(str, Enum):
    SEND = "send"
    ALERT = "alert"


class DeliveryMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    INTERNAL = "internal"


class Operator(str, Enum):
    EQUALS = "equals"
    GTE = "gte"


class SuppressionMode(str, Enum):
    ONCE_EVER = "once_ever"
    ONCE_PER_CALENDAR_DAY = "once_per_calendar_day"
    NONE = "none"
