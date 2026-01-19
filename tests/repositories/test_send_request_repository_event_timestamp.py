from datetime import datetime, timezone

from src.marketing_messaging_service.models.send_request import SendRequest
from src.marketing_messaging_service.repositories.send_request_repository import (
    SendRequestRepository,
)


def test_exists_for_user_and_template_in_day_so_far_uses_event_timestamp_strict_bounds(db_session):
    repo = SendRequestRepository()

    window_ts = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    window_start = window_ts.replace(hour=0, minute=0, second=0, microsecond=0)

    # Boundary rows should NOT match (strict inequalities)
    db_session.add_all(
        [
            SendRequest(
                user_id="u1",
                template_name="T1",
                channel="email",
                reason="rule:test",
                event_timestamp=window_start,
            ),
            SendRequest(
                user_id="u1",
                template_name="T1",
                channel="email",
                reason="rule:test",
                event_timestamp=window_ts,
            ),
        ]
    )
    db_session.commit()

    assert (
        repo.exists_for_user_and_template_in_day_so_far(
            db=db_session,
            user_id="u1",
            template_name="T1",
            provided_ts=window_ts,
        )
        is False
    )

    # Now add a row strictly inside (window_start, provided_ts)
    db_session.add(
        SendRequest(
            user_id="u1",
            template_name="T1",
            channel="email",
            reason="rule:test",
            event_timestamp=datetime(2025, 1, 1, 1, 0, tzinfo=timezone.utc),
        )
    )
    db_session.commit()

    assert (
        repo.exists_for_user_and_template_in_day_so_far(
            db=db_session,
            user_id="u1",
            template_name="T1",
            provided_ts=window_ts,
        )
        is True
    )


def test_exists_for_user_and_template_in_day_so_far_ignores_rows_without_event_timestamp(db_session):
    repo = SendRequestRepository()

    # Legacy/ad-hoc row: no event_timestamp.
    db_session.add(
        SendRequest(
            user_id="u2",
            template_name="T2",
            channel="email",
            reason="rule:test",
            decided_at=datetime(2025, 1, 3, 8, 0, tzinfo=timezone.utc),
        )
    )
    db_session.commit()

    # Since we only use event_timestamp, this should NOT be considered "already sent".
    assert (
        repo.exists_for_user_and_template_in_day_so_far(
            db=db_session,
            user_id="u2",
            template_name="T2",
            provided_ts=datetime(2025, 1, 3, 10, 0, tzinfo=timezone.utc),
        )
        is False
    )
