from datetime import datetime, timezone

from src.marketing_messaging_service.repositories.event_repository import EventRepository
from src.marketing_messaging_service.schemas.event import EventIn, UserTraitsIn
from src.marketing_messaging_service.services.event_processing_service import EventProcessingService
from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits


class _DummySendRequestRepository:
    def add(self, db, send_request):
        return send_request


class _DummySuppressionRepository:
    def add(self, db, suppression):
        return suppression


def test_process_event_persists_event_and_traits(db_session):
    service = EventProcessingService(
        event_repository=EventRepository(),
        send_request_repository=_DummySendRequestRepository(),
        suppression_repository=_DummySuppressionRepository(),
    )

    payload = EventIn(
        user_id="u_12345",
        event_type="payment_failed",
        event_timestamp=datetime(2025, 10, 31, 19, 22, 11, tzinfo=timezone.utc),
        properties={
            "amount": 1425.0,
            "attempt_number": 2,
            "failure_reason": "INSUFFICIENT_FUNDS",
            "extra_field": "allowed",
        },
        user_traits=UserTraitsIn(
            email="maria@example.com",
            country="PT",
            marketing_opt_in=True,
            risk_segment="MEDIUM",
        ),
    )

    saved_event = service.process_event(db_session, payload)

    db_session.flush()

    event_row = db_session.query(Event).filter(Event.id == saved_event.id).first()
    assert event_row is not None
    assert event_row.user_id == "u_12345"
    assert event_row.event_type == "payment_failed"
    assert event_row.properties is not None
    assert event_row.properties["failure_reason"] == "INSUFFICIENT_FUNDS"
    assert event_row.properties["extra_field"] == "allowed"

    traits_row = db_session.query(UserTraits).filter(UserTraits.event_id == saved_event.id).first()
    assert traits_row is not None
    assert traits_row.email == "maria@example.com"
    assert traits_row.country == "PT"
    assert traits_row.marketing_opt_in is True
    assert traits_row.risk_segment == "MEDIUM"
