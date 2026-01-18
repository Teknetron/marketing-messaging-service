from datetime import datetime, timedelta

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.send_request import SendRequest
from src.marketing_messaging_service.models.suppression import Suppression
from src.marketing_messaging_service.repositories.event_repository import EventRepository
from src.marketing_messaging_service.repositories.send_request_repository import SendRequestRepository
from src.marketing_messaging_service.repositories.suppression_repository import SuppressionRepository
from src.marketing_messaging_service.services.audit_service import AuditService


def _make_audit_service():
    return AuditService(
        event_repository=EventRepository(),
        send_request_repository=SendRequestRepository(),
        suppression_repository=SuppressionRepository(),
    )


def test_audit_log_merges_event_send_and_suppression(db_session):
    service = _make_audit_service()

    now = datetime.utcnow()

    event = Event(
        user_id="user_1",
        event_type="payment_failed",
        event_timestamp=now,
    )
    db_session.add(event)
    db_session.flush()

    send = SendRequest(
        user_id="user_1",
        template_name="insufficient_funds",
        channel="email",
        reason="rule:test",
        decided_at=now + timedelta(seconds=1),
    )

    suppression = Suppression(
        user_id="user_1",
        template_name="insufficient_funds",
        suppression_reason="once_per_calendar_day",
        event_id=event.id,
        decided_at=now + timedelta(seconds=2),
    )

    db_session.add_all([send, suppression])
    db_session.commit()

    audit_log = service.get_audit_log(db_session, "user_1")

    kinds = [item.kind for item in audit_log.items]

    assert "event" in kinds
    assert "send_request" in kinds
    assert "suppression" in kinds


def test_audit_log_is_sorted_newest_first(db_session):
    service = _make_audit_service()

    base_time = datetime.utcnow()

    event_old = Event(
        user_id="user_2",
        event_type="signup_completed",
        event_timestamp=base_time,
    )

    event_new = Event(
        user_id="user_2",
        event_type="payment_initiated",
        event_timestamp=base_time + timedelta(hours=1),
    )

    db_session.add_all([event_old, event_new])
    db_session.commit()

    audit_log = service.get_audit_log(db_session, "user_2")

    assert audit_log.items[0].timestamp >= audit_log.items[1].timestamp


def test_send_request_outcome_is_allow_or_alert(db_session):
    service = _make_audit_service()

    now = datetime.utcnow()

    send_allow = SendRequest(
        user_id="user_3",
        template_name="welcome",
        channel="email",
        reason="rule:welcome",
        decided_at=now,
    )

    send_alert = SendRequest(
        user_id="user_3",
        template_name="fraud_alert",
        channel="internal",
        reason="rule:fraud",
        decided_at=now + timedelta(seconds=1),
    )

    db_session.add_all([send_allow, send_alert])
    db_session.commit()

    audit_log = service.get_audit_log(db_session, "user_3")

    outcomes = {item.channel: item.outcome for item in audit_log.items if item.kind == "send_request"}

    assert outcomes["email"] == "allow"
    assert outcomes["internal"] == "alert"


def test_suppression_has_suppress_outcome(db_session):
    service = _make_audit_service()

    now = datetime.utcnow()

    event = Event(
        user_id="user_4",
        event_type="payment_failed",
        event_timestamp=now,
    )
    db_session.add(event)
    db_session.flush()

    suppression = Suppression(
        user_id="user_4",
        template_name="insufficient_funds",
        suppression_reason="once_ever",
        event_id=event.id,
        decided_at=now,
    )

    db_session.add(suppression)
    db_session.commit()

    audit_log = service.get_audit_log(db_session, "user_4")

    suppression_items = [i for i in audit_log.items if i.kind == "suppression"]

    assert len(suppression_items) == 1
    assert suppression_items[0].outcome == "suppress"


def test_audit_log_filters_by_user_id(db_session):
    service = _make_audit_service()

    now = datetime.utcnow()

    event_user_a = Event(
        user_id="user_a",
        event_type="signup_completed",
        event_timestamp=now,
    )

    event_user_b = Event(
        user_id="user_b",
        event_type="signup_completed",
        event_timestamp=now,
    )

    db_session.add_all([event_user_a, event_user_b])
    db_session.commit()

    audit_a = service.get_audit_log(db_session, "user_a")
    audit_b = service.get_audit_log(db_session, "user_b")

    assert all(item.event_type == "signup_completed" for item in audit_a.items)
    assert all(item.event_type == "signup_completed" for item in audit_b.items)

    assert audit_a.user_id == "user_a"
    assert audit_b.user_id == "user_b"
