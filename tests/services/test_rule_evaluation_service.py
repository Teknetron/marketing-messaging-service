import tempfile
import yaml
from datetime import datetime, timezone, timedelta

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits
from src.marketing_messaging_service.repositories.event_repository import EventRepository
from src.marketing_messaging_service.services.rule_evaluation_service import RuleEvaluationService


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def write_rules_to_temp_file(rules: dict) -> str:
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(rules, f)
    return path


def create_event(db, user_id, event_type, timestamp, properties=None, traits=None):
    repo = EventRepository()

    event = Event(
        user_id=user_id,
        event_type=event_type,
        event_timestamp=timestamp,
        properties=properties or {},
    )

    if traits is not None:
        event.user_traits = UserTraits(**traits)

    return repo.add(db, event)


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_rule_1_welcome_email(db_session):
    rules = {
        "rules": [
            {
                "name": "welcome_email",
                "description": "",
                "enabled": True,
                "trigger": {"event_type": "signup_completed"},
                "conditions": {
                    "all": [
                        {"field": "user_traits.marketing_opt_in", "operator": "equals", "value": True}
                    ]
                },
                "action": {"type": "send", "template_name": "WELCOME_EMAIL", "delivery_method": "email"},
                "suppression": {"mode": "once_ever"}
            }
        ]
    }

    path = write_rules_to_temp_file(rules)
    repo = EventRepository()
    service = RuleEvaluationService(event_repository=repo, rules_path=path)

    event = create_event(
        db_session,
        "u1",
        "signup_completed",
        datetime(2025, 1, 1, tzinfo=timezone.utc),
        traits={"email": "x", "country": "PT", "marketing_opt_in": True, "risk_segment": "LOW"}
    )

    decision = service.evaluate(db_session, event, event.user_traits)

    assert decision.action_type == "send"
    assert decision.template_name == "WELCOME_EMAIL"
    assert decision.delivery_method == "email"
    assert decision.suppression_mode == "once_ever"
    assert decision.matched_rule == "welcome_email"


def test_rule_2_prior_event_within_24h(db_session):
    rules = {
        "rules": [
            {
                "name": "bank_link_nudge",
                "enabled": True,
                "trigger": {"event_type": "link_bank_success"},
                "conditions": {
                    "all": [
                        {"prior_event": {"event_type": "signup_completed", "hours": 24}}
                    ]
                },
                "action": {"type": "send", "template_name": "BANK_LINK_NUDGE_SMS", "delivery_method": "sms"},
                "suppression": {"mode": "once_ever"}
            }
        ]
    }

    path = write_rules_to_temp_file(rules)
    repo = EventRepository()
    service = RuleEvaluationService(event_repository=repo, rules_path=path)

    # First event: signup
    signup = create_event(
        db_session,
        "u2",
        "signup_completed",
        datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
    )

    # Second: bank link within 24 hours
    link = create_event(
        db_session,
        "u2",
        "link_bank_success",
        datetime(2025, 1, 2, 9, 0, tzinfo=timezone.utc),
    )

    decision = service.evaluate(db_session, link, None)

    assert decision.action_type == "send"
    assert decision.template_name == "BANK_LINK_NUDGE_SMS"
    assert decision.matched_rule == "bank_link_nudge"


def test_rule_3_insufficient_funds(db_session):
    rules = {
        "rules": [
            {
                "name": "insufficient_funds_email",
                "enabled": True,
                "trigger": {"event_type": "payment_failed"},
                "conditions": {
                    "all": [
                        {"field": "properties.failure_reason", "operator": "equals", "value": "INSUFFICIENT_FUNDS"}
                    ]
                },
                "action": {"type": "send", "template_name": "INSUFFICIENT_FUNDS_EMAIL", "delivery_method": "email"},
                "suppression": {"mode": "once_per_calendar_day"}
            }
        ]
    }

    path = write_rules_to_temp_file(rules)
    repo = EventRepository()
    service = RuleEvaluationService(event_repository=repo, rules_path=path)

    event = create_event(
        db_session,
        "u3",
        "payment_failed",
        datetime(2025, 1, 3, tzinfo=timezone.utc),
        properties={"failure_reason": "INSUFFICIENT_FUNDS"},
    )

    decision = service.evaluate(db_session, event, None)

    assert decision.action_type == "send"
    assert decision.template_name == "INSUFFICIENT_FUNDS_EMAIL"


def test_rule_4_high_risk_alert(db_session):
    rules = {
        "rules": [
            {
                "name": "high_risk_alert",
                "enabled": True,
                "trigger": {"event_type": "payment_failed"},
                "conditions": {
                    "all": [
                        {"field": "properties.attempt_number", "operator": "gte", "value": 3}
                    ]
                },
                "action": {"type": "alert", "template_name": "HIGH_RISK_ALERT", "delivery_method": "internal"},
                "suppression": {"mode": "none"}
            }
        ]
    }

    path = write_rules_to_temp_file(rules)
    repo = EventRepository()
    service = RuleEvaluationService(event_repository=repo, rules_path=path)

    event = create_event(
        db_session,
        "u4",
        "payment_failed",
        datetime(2025, 1, 4, tzinfo=timezone.utc),
        properties={"attempt_number": 3},
    )

    decision = service.evaluate(db_session, event, None)

    assert decision.action_type == "alert"
    assert decision.template_name == "HIGH_RISK_ALERT"
    assert decision.delivery_method == "internal"
    assert decision.suppression_mode == "none"
    assert decision.matched_rule == "high_risk_alert"


def test_no_match(db_session):
    rules = {
        "rules": [
            {
                "name": "welcome_email",
                "enabled": True,
                "trigger": {"event_type": "signup_completed"},
                "conditions": {
                    "all": [
                        {"field": "user_traits.marketing_opt_in", "operator": "equals", "value": True}
                    ]
                },
                "action": {"type": "send", "template_name": "WELCOME_EMAIL", "delivery_method": "email"},
                "suppression": {"mode": "once_ever"}
            }
        ]
    }

    path = write_rules_to_temp_file(rules)
    repo = EventRepository()
    service = RuleEvaluationService(event_repository=repo, rules_path=path)

    # Wrong event type → no match
    event = create_event(
        db_session,
        "u5",
        "payment_failed",
        datetime(2025, 1, 5, tzinfo=timezone.utc),
    )

    decision = service.evaluate(db_session, event, None)

    assert decision.action_type == "none"
    assert decision.matched_rule is None
