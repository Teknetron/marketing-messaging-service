from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from src.marketing_messaging_service.infrastructure.database import create_session
from src.marketing_messaging_service.providers.fake_providers import FakeMessagingProvider
from src.marketing_messaging_service.repositories import EventRepository
from src.marketing_messaging_service.repositories import SendRequestRepository
from src.marketing_messaging_service.repositories import SuppressionRepository
from src.marketing_messaging_service.repositories.decision_repository import DecisionRepository
from src.marketing_messaging_service.schemas.event import EventIn
from src.marketing_messaging_service.schemas.event import EventProcessingResult
from src.marketing_messaging_service.services.event_processing_service import EventProcessingService
from src.marketing_messaging_service.services.rule_evaluation_service import RuleEvaluationService
from src.marketing_messaging_service.services.suppression_service import SuppressionService

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    with create_session() as session:
        yield session


event_repository = EventRepository()
send_request_repository = SendRequestRepository()
suppression_repository = SuppressionRepository()
decision_repository = DecisionRepository()


rule_evaluation_service = RuleEvaluationService(event_repository=event_repository)
suppression_service = SuppressionService(
    suppression_repository=suppression_repository,
    send_request_repository=send_request_repository
)
messaging_provider = FakeMessagingProvider()

event_processing_service = EventProcessingService(
    event_repository=event_repository,
    send_request_repository=send_request_repository,
    suppression_repository=suppression_repository,
    rule_evaluation_service=rule_evaluation_service,
    suppression_service=suppression_service,
    decision_repository=decision_repository,
    messaging_provider=messaging_provider,
)


@router.post("/", response_model=EventProcessingResult)
def ingest_event(payload: EventIn, db: Session = Depends(get_db)):
    saved_event, decision, outcome, channel, reason = event_processing_service.process_event(db, payload)

    return EventProcessingResult(
        event_id=saved_event.id,
        user_id=saved_event.user_id,
        event_type=saved_event.event_type,
        matched_rule=decision.matched_rule,
        action_type=decision.action_type,
        template_name=decision.template_name,
        channel=channel,
        outcome=outcome,
        reason=reason,
    )
