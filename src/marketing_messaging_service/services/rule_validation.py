from typing import Any

from src.marketing_messaging_service.services.enums import (
    ActionType,
    DeliveryMethod,
    Operator,
    SuppressionMode,
)

_ALLOWED_FIELD_PREFIXES = ("properties.", "user_traits.")

def validate_rules_config(data: Any) -> list[dict[str, Any]]:
    errors: list[str] = []

    if not isinstance(data, dict):
        raise ValueError("Invalid rules.yaml: root must be a mapping (dict).")

    rules = data.get("rules")
    if not isinstance(rules, list):
        raise ValueError("Invalid rules.yaml: 'rules' must be a list.")

    validated_rules: list[dict[str, Any]] = []

    for idx, rule in enumerate(rules):
        rule_path = f"rules[{idx}]"

        if not isinstance(rule, dict):
            errors.append(f"{rule_path}: must be a dict.")
            continue

        name = rule.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{rule_path}.name: required non-empty string.")

        enabled = rule.get("enabled", True)
        if not isinstance(enabled, bool):
            errors.append(f"{rule_path}.enabled: must be boolean.")

        trigger = rule.get("trigger")
        if not isinstance(trigger, dict):
            errors.append(f"{rule_path}.trigger: required dict.")
        else:
            event_type = trigger.get("event_type")
            if not isinstance(event_type, str) or not event_type.strip():
                errors.append(f"{rule_path}.trigger.event_type: required non-empty string.")

        conditions = rule.get("conditions")
        if not isinstance(conditions, dict):
            errors.append(f"{rule_path}.conditions: required dict.")
        else:
            all_conditions = conditions.get("all")
            if not isinstance(all_conditions, list):
                errors.append(f"{rule_path}.conditions.all: required list.")
            else:
                for cidx, condition in enumerate(all_conditions):
                    cpath = f"{rule_path}.conditions.all[{cidx}]"
                    _validate_condition(condition, cpath, errors)

        action = rule.get("action")
        if not isinstance(action, dict):
            errors.append(f"{rule_path}.action: required dict.")
        else:
            _validate_action(action, rule_path, errors)

        suppression = rule.get("suppression")
        if suppression is None:
            rule["suppression"] = {"mode": SuppressionMode.NONE.value}
        elif not isinstance(suppression, dict):
            errors.append(f"{rule_path}.suppression: must be dict if provided.")
        else:
            mode = suppression.get("mode", SuppressionMode.NONE.value)
            if mode not in {m.value for m in SuppressionMode}:
                allowed = sorted(m.value for m in SuppressionMode)
                errors.append(f"{rule_path}.suppression.mode: must be one of {allowed}.")

        validated_rules.append(rule)

    if errors:
        message = "Invalid rules.yaml:\n" + "\n".join(f"- {e}" for e in errors)
        raise ValueError(message)

    return validated_rules


def _validate_condition(condition: Any, path: str, errors: list[str]) -> None:
    if not isinstance(condition, dict):
        errors.append(f"{path}: must be dict.")
        return

    has_field = "field" in condition
    has_prior = "prior_event" in condition

    if has_field and has_prior:
        errors.append(f"{path}: must contain only one of 'field' or 'prior_event'.")
        return

    if has_field:
        field_path = condition.get("field")
        operator = condition.get("operator")

        if not isinstance(field_path, str) or not field_path.strip():
            errors.append(f"{path}.field: required non-empty string.")
        else:
            if not field_path.startswith(_ALLOWED_FIELD_PREFIXES):
                errors.append(f"{path}.field: must start with one of {list(_ALLOWED_FIELD_PREFIXES)}.")

        if operator not in {op.value for op in Operator}:
            allowed = sorted(op.value for op in Operator)
            errors.append(f"{path}.operator: must be one of {allowed}.")

        if "value" not in condition:
            errors.append(f"{path}.value: required.")
        return

    if has_prior:
        prior = condition.get("prior_event")
        if not isinstance(prior, dict):
            errors.append(f"{path}.prior_event: must be dict.")
            return

        prior_event_type = prior.get("event_type")
        hours = prior.get("hours")

        if not isinstance(prior_event_type, str) or not prior_event_type.strip():
            errors.append(f"{path}.prior_event.event_type: required non-empty string.")
        if not isinstance(hours, int) or hours <= 0:
            errors.append(f"{path}.prior_event.hours: required positive int.")
        return

    errors.append(f"{path}: must contain 'field' or 'prior_event'.")


def _validate_action(action: dict[str, Any], rule_path: str, errors: list[str]) -> None:
    action_type = action.get("type")

    if action_type not in {t.value for t in ActionType}:
        allowed = sorted(t.value for t in ActionType)
        errors.append(f"{rule_path}.action.type: must be one of {allowed}.")

    template_name = action.get("template_name")
    if not isinstance(template_name, str) or not template_name.strip():
        errors.append(f"{rule_path}.action.template_name: required non-empty string.")

    delivery_method = action.get("delivery_method")
    if delivery_method not in {d.value for d in DeliveryMethod}:
        allowed = sorted(d.value for d in DeliveryMethod)
        errors.append(f"{rule_path}.action.delivery_method: must be one of {allowed}.")

    if action_type == ActionType.ALERT.value and delivery_method != DeliveryMethod.INTERNAL.value:
        errors.append(
            f"{rule_path}.action.delivery_method: must be '{DeliveryMethod.INTERNAL.value}' when action.type is '{ActionType.ALERT.value}'."
        )
