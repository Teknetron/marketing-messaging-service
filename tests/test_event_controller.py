from fastapi.testclient import TestClient

from src.marketing_messaging_service.controllers.endpoints import app
from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits
from src.marketing_messaging_service.controllers import event_controller


def test_post_events_persists_and_returns_accepted(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[event_controller.get_db] = override_get_db

    client = TestClient(app)

    payload = {
        "user_id": "u_999",
        "event_type": "signup_completed",
        "event_timestamp": "2025-10-31T19:22:11Z",
        "properties": {"hello": "world"},
        "user_traits": {
            "email": "u999@example.com",
            "country": "PT",
            "marketing_opt_in": True,
            "risk_segment": "LOW",
        },
    }

    resp = client.post("/events/", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"status": "accepted"}

    events = db_session.query(Event).filter(Event.user_id == "u_999").all()
    assert len(events) == 1

    traits = db_session.query(UserTraits).filter(UserTraits.event_id == events[0].id).all()
    assert len(traits) == 1
    assert traits[0].email == "u999@example.com"
