from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits
from src.marketing_messaging_service.repositories.interfaces import (
    IEventRepository,
    ISendRequestRepository,
    ISuppressionRepository,
)
from src.marketing_messaging_service.schemas.event import EventIn


class EventProcessingService:
    def __init__(
        self,
        event_repository: IEventRepository,
        send_request_repository: ISendRequestRepository,
        suppression_repository: ISuppressionRepository,
    ):
        self.event_repository = event_repository
        self.send_request_repository = send_request_repository
        self.suppression_repository = suppression_repository

    def process_event(self, db: Session, payload: EventIn) -> Event:
        """
        Step 5.1:
        - Persist Event (including dynamic JSON properties)
        - Persist optional UserTraits (1:1)
        Business logic (rules/dedup/sends) is added in later steps.
        """
        event = Event(
            user_id=payload.user_id,
            event_type=payload.event_type,
            event_timestamp=payload.event_timestamp,
            properties=payload.properties,
        )

        saved_event = self.event_repository.add(db, event)

        if payload.user_traits is not None:
            traits = UserTraits(
                event_id=saved_event.id,
                email=payload.user_traits.email,
                country=payload.user_traits.country,
                marketing_opt_in=payload.user_traits.marketing_opt_in,
                risk_segment=payload.user_traits.risk_segment,
            )
            db.add(traits)

        db.flush()
        return saved_event
