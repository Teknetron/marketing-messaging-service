from pathlib import Path
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
        self.rules_path = self._resolve_config_path(rules_path)
        self._rules = None

    def evaluate(self, db: Session, event: Event, user_traits: UserTraits | None) -> RuleDecision:
        """Find the first matching rule and return its decision."""
        rules = self._load_rules()

        for rule in rules:
            if self._rule_matches(rule, db, event, user_traits):
                return self._create_decision(rule)

        # No rules matched
        return RuleDecision(
            action_type="none",
            reason="No matching rule",
        )

    def _resolve_config_path(self, rules_path: str | None) -> str:
        """Figure out where the rules.yaml file is."""
        project_root = Path(__file__).parent.parent.parent.parent

        if rules_path:
            return rules_path
        if os.environ.get("RULES_CONFIG_PATH"):
            return str(project_root / os.environ.get("RULES_CONFIG_PATH"))
        return str(project_root / "config" / "rules.yaml")

    def _load_rules(self) -> list[Rule]:
        """Load rules from YAML file (only once)."""
        if self._rules is not None:
            return self._rules

        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self._rules = [Rule(**rule_data) for rule_data in data.get("rules", [])]
        return self._rules

    def _rule_matches(self, rule: Rule, db: Session, event: Event, user_traits: UserTraits | None) -> bool:
        """Check if rule matches the event."""
        # Rule must be enabled
        if not rule.enabled:
            return False

        # Event type must match trigger
        if rule.trigger.get("event_type") != event.event_type:
            return False

        # All conditions must pass
        return self._check_all_conditions(rule, db, event, user_traits)

    def _check_all_conditions(self, rule: Rule, db: Session, event: Event, user_traits: UserTraits | None) -> bool:
        """Check if all conditions in the rule pass."""
        conditions = rule.conditions.get("all", [])

        for condition in conditions:
            if "field" in condition:
                if not self._check_field_condition(condition, event, user_traits):
                    return False
            elif "prior_event" in condition:
                if not self._check_prior_event_condition(condition["prior_event"], db, event):
                    return False
            else:
                return False  # Unknown condition type

        return True

    def _check_field_condition(self, condition: dict, event: Event, user_traits: UserTraits | None) -> bool:
        """Check if a field condition passes."""
        field_path = condition["field"]
        operator = condition["operator"]
        expected_value = condition.get("value")

        actual_value = self._get_field_value(field_path, event, user_traits)

        if operator == "equals":
            return actual_value == expected_value
        elif operator == "gte":
            return actual_value is not None and actual_value >= expected_value
        else:
            return False  # Unknown operator

    def _check_prior_event_condition(self, condition: dict, db: Session, event: Event) -> bool:
        """Check if a prior event condition passes."""
        event_type = condition["event_type"]
        hours_limit = condition["hours"]

        prior_event = self.event_repository.get_latest_by_user_and_type(
            db=db,
            user_id=event.user_id,
            event_type=event_type,
        )

        if prior_event is None:
            return False

        time_diff = event.event_timestamp - prior_event.event_timestamp
        max_time_diff = timedelta(hours=hours_limit)

        return time_diff <= max_time_diff

    def _get_field_value(self, field_path: str, event: Event, user_traits: UserTraits | None):
        """Get the actual value from event or user_traits."""
        if field_path.startswith("event."):
            field_name = field_path.replace("event.", "")
            return getattr(event, field_name, None)

        elif field_path.startswith("user_traits."):
            if user_traits is None:
                return None
            field_name = field_path.replace("user_traits.", "")
            return getattr(user_traits, field_name, None)

        elif field_path.startswith("properties."):
            property_key = field_path.replace("properties.", "")
            properties = event.properties or {}
            return properties.get(property_key)

        else:
            return None

    def _create_decision(self, rule: Rule) -> RuleDecision:
        """Create a RuleDecision from a matching rule."""
        return RuleDecision(
            action_type=rule.action["type"],
            template_name=rule.action.get("template_name"),
            delivery_method=rule.action.get("delivery_method"),
            suppression_mode=rule.suppression.get("mode"),
            matched_rule=rule.name,
            reason=f"Matched rule: {rule.name}",
        )