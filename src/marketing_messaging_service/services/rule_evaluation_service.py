import yaml
import os
from datetime import timedelta

from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits
from src.marketing_messaging_service.repositories.interfaces import IEventRepository
from src.marketing_messaging_service.services.rule_models import Rule, RuleDecision


class RuleEvaluationService:
    def __init__(self, event_repository: IEventRepository, rules_path: str | None = None):
        self.event_repository = event_repository
        self.rules_path = (
            rules_path
            or os.environ.get("RULES_CONFIG_PATH")
            or "src/marketing_messaging_service/config/rules.yaml"
        )
        self._rules: list[Rule] | None = None

    def evaluate(self, db: Session, event: Event, user_traits: UserTraits | None) -> RuleDecision:
        for rule in self._load_rules():
            if not rule.enabled:
                continue
            if rule.trigger.get("event_type") != event.event_type:
                continue

            ok, reason = self._conditions_match(db, rule, event, user_traits)
            if not ok:
                continue

            return RuleDecision(
                action_type=rule.action["type"],
                template_name=rule.action.get("template_name"),
                delivery_method=rule.action.get("delivery_method"),
                suppression_mode=rule.suppression.get("mode"),
                matched_rule=rule.name,
                reason=reason,
            )

        return RuleDecision(
            action_type="none",
            reason="No matching rule",
        )


    def _load_rules(self) -> list[Rule]:
        if self._rules is not None:
            return self._rules

        with open(self.rules_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        self._rules = [Rule(**r) for r in raw.get("rules", [])]
        return self._rules

    # ---------------------------------------------
    # Condition evaluation
    # ---------------------------------------------

    def _conditions_match(self, db: Session, rule: Rule, event: Event, user_traits: UserTraits | None) -> tuple[bool, str]:
        for cond in rule.conditions.get("all", []):

            # Field condition
            if "field" in cond:
                if not self._field_condition(cond, event, user_traits):
                    return False, f"Rule {rule.name}: field condition failed"
                continue

            # Prior event condition
            if "prior_event" in cond:
                if not self._prior_event_condition(db, cond["prior_event"], event):
                    return False, f"Rule {rule.name}: prior event condition failed"
                continue

            return False, f"Rule {rule.name}: unsupported condition"

        return True, f"Matched rule: {rule.name}"

    # ---------------------------------------------
    # Field condition evaluation
    # ---------------------------------------------

    def _resolve_field(self, path: str, event: Event, traits: UserTraits | None):
        if path.startswith("event."):
            return getattr(event, path[6:], None)

        if path.startswith("user_traits."):
            return getattr(traits, path[12:], None) if traits else None

        if path.startswith("properties."):
            key = path[11:]
            return (event.properties or {}).get(key)

        return None

    def _field_condition(self, cond: dict, event: Event, traits: UserTraits | None) -> bool:
        actual = self._resolve_field(cond["field"], event, traits)
        op = cond["operator"]
        val = cond.get("value")

        if op == "equals":
            return actual == val

        if op == "gte":
            return actual is not None and actual >= val

        return False

    # ---------------------------------------------
    # Prior event condition evaluation
    # ---------------------------------------------

    def _prior_event_condition(self, db, cond: dict, event: Event) -> bool:
        event_type = cond["event_type"]
        hours = cond["hours"]

        prior = self.event_repository.get_latest_by_user_and_type(
            db=db,  # placeholder, db passed separately
            user_id=event.user_id,
            event_type=event_type,
        )

        if prior is None:
            return False

        window = timedelta(hours=hours)
        return (event.event_timestamp - prior.event_timestamp) <= window
