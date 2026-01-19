from typing import Any

from pydantic import BaseModel


class Rule(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True

    trigger: dict[str, Any]
    conditions: dict[str, list[dict[str, Any]]]
    action: dict[str, Any]
    suppression: dict[str, Any]


class RuleDecision(BaseModel):
    action_type: str  # "send" | "alert" | "none"
    template_name: str | None = None
    delivery_method: str | None = None
    suppression_mode: str | None = None
    matched_rule: str | None = None
    reason: str
