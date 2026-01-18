from sqlalchemy.orm import Session

from src.marketing_messaging_service.models import SendRequest, Suppression
from src.marketing_messaging_service.models.decision import Decision
from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.user_traits import UserTraits
from src.marketing_messaging_service.providers.interfaces import IMessagingProvider
from src.marketing_messaging_service.repositories.interfaces import IEventRepository, ISendRequestRepository, \
    ISuppressionRepository, IDecisionRepository
from src.marketing_messaging_service.schemas.event import EventIn
from src.marketing_messaging_service.services.rule_evaluation_service import RuleEvaluationService
from src.marketing_messaging_service.services.suppression_service import SuppressionService


class EventProcessingService:
    def __init__(
        self,
        event_repository: IEventRepository,
        send_request_repository: ISendRequestRepository,
        suppression_repository: ISuppressionRepository,
        rule_evaluation_service: RuleEvaluationService,
        suppression_service: SuppressionService,
        messaging_provider: IMessagingProvider,
        decision_repository: IDecisionRepository,
    ):
        self.event_repository = event_repository
        self.send_request_repository = send_request_repository
        self.suppression_repository = suppression_repository
        self.rule_evaluation_service = rule_evaluation_service
        self.suppression_service = suppression_service
        self.messaging_provider = messaging_provider

    def process_event(self, db: Session, payload: EventIn):
        event = Event(
            user_id=payload.user_id,
            event_type=payload.event_type,
            event_timestamp=payload.event_timestamp,
            properties=payload.properties,
        )

        if payload.user_traits is not None:
            event.user_traits = UserTraits(
                email=payload.user_traits.email,
                country=payload.user_traits.country,
                marketing_opt_in=payload.user_traits.marketing_opt_in,
                risk_segment=payload.user_traits.risk_segment,
            )

        saved_event = self.event_repository.add(db, event)

        decision = self.rule_evaluation_service.evaluate(
            db=db,
            event=saved_event,
            user_traits=saved_event.user_traits,
        )

        outcome, suppression_reason = self.suppression_service.evaluate(
            db=db,
            user_id=saved_event.user_id,
            decision=decision,
        )

        if outcome == "allow":
            send_request = SendRequest(
                user_id=saved_event.user_id,
                template_name=decision.template_name,
                channel=decision.delivery_method,
                reason=f"rule:{decision.matched_rule}",
            )
            self.send_request_repository.add(db, send_request)
            # TODO: add new bool field to send request "send_message_success"
            self.messaging_provider.send_message(
                user_id=saved_event.user_id,
                template_name=decision.template_name,
                channel=decision.delivery_method,
                reason=f"rule:{decision.matched_rule}",
            )

        elif outcome == "alert":
            send_request = SendRequest(
                user_id=saved_event.user_id,
                template_name=decision.template_name,
                channel="internal",
                reason=f"rule:{decision.matched_rule}",
            )
            self.send_request_repository.add(db, send_request)
            # TODO: add new bool field to send request "send_message_success"
            self.messaging_provider.send_message(
                user_id=saved_event.user_id,
                template_name=decision.template_name,
                channel="internal",
                reason=f"rule:{decision.matched_rule}",
            )

        elif outcome == "suppress":
            suppression = Suppression(
                user_id=saved_event.user_id,
                template_name=decision.template_name,
                suppression_reason=suppression_reason,
                event_id=saved_event.id,
            )
            self.suppression_repository.add(db, suppression)

        channel = "internal" if outcome == "alert" else decision.delivery_method
        reason = suppression_reason if outcome == "suppress" else decision.reason

        decision_row = Decision(
            user_id=saved_event.user_id,
            event_id=saved_event.id,
            event_type=saved_event.event_type,
            matched_rule=decision.matched_rule,
            action_type=decision.action_type,
            outcome=outcome,
            reason=reason,  # e.g. "matched rule X" / "suppressed by once_ever"
            template_name=decision.template_name,
            channel=decision.delivery_method if decision.delivery_method else None,
        )

        self.decision_repository.add(db, decision_row)

        return saved_event, decision, outcome, channel, reason
