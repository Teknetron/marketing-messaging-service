from datetime import datetime, timezone

from src.marketing_messaging_service.repositories.event_repository import EventRepository
from src.marketing_messaging_service.repositories.send_request_repository import SendRequestRepository
from src.marketing_messaging_service.repositories.suppression_repository import SuppressionRepository
from src.marketing_messaging_service.services.event_processing_service import EventProcessingService
from src.marketing_messaging_service.services.rule_evaluation_service import RuleEvaluationService
from src.marketing_messaging_service.schemas.event import EventIn, UserTraitsIn
from src.marketing_messaging_service.models.event import Event


def _build_service():
    event_repo = EventRepository()
    send_repo = SendRequestRepository()
    suppression_repo = SuppressionRepository()
    rule_eval = RuleEvaluationService(event_repository=event_repo)

    return EventProcessingService(
        event_repository=event_repo,
        send_request_repository=send_repo,
        suppression_repository=suppression_repo,
        rule_evaluation_service=rule_eval,
    )


def test_process_event_returns_decision_when_rule_matches(db_session):
    service = _build_service()

    payload = EventIn(
        user_id="user_step_5_3",
        event_type="signup_completed",
        event_timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        properties={},
        user_traits=UserTraitsIn(
            email="test@example.com",
            country="PT",
            marketing_opt_in=True,
            risk_segment="LOW",
        ),
    )

    saved_event, decision = service.process_event(db_session, payload)

    # Event persisted
    assert isinstance(saved_event, Event)
    assert saved_event.id is not None
    assert saved_event.user_id == "user_step_5_3"

    # Rule decision returned
    assert decision is not None
    assert decision.action_type == "send"
    assert decision.matched_rule is not None


def test_process_event_returns_none_decision_when_no_rule_matches(db_session):
    service = _build_service()

    payload = EventIn(
        user_id="user_no_match",
        event_type="some_unknown_event",
        event_timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
        properties={},
        user_traits=None,
    )

    saved_event, decision = service.process_event(db_session, payload)

    assert saved_event.id is not None
    assert decision.action_type == "none"
    assert decision.matched_rule is None


def test_user_traits_are_persisted_and_used(db_session):
    service = _build_service()

    payload = EventIn(
        user_id="user_traits_test",
        event_type="signup_completed",
        event_timestamp=datetime(2025, 1, 3, tzinfo=timezone.utc),
        properties={},
        user_traits=UserTraitsIn(
            email="traits@example.com",
            country="ES",
            marketing_opt_in=True,
            risk_segment="MEDIUM",
        ),
    )

    saved_event, decision = service.process_event(db_session, payload)

    assert saved_event.user_traits is not None
    assert saved_event.user_traits.email == "traits@example.com"
    assert decision.action_type == "send"
