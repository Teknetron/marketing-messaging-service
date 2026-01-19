from sqlalchemy.orm import Session

from src.marketing_messaging_service.models import Event
from src.marketing_messaging_service.repositories.interfaces import (
    ISendRequestRepository, ISuppressionRepository)
from src.marketing_messaging_service.services.rule_models import RuleDecision


class SuppressionService:
    def __init__(
        self,
        send_request_repository: ISendRequestRepository,
        suppression_repository: ISuppressionRepository,
    ):
        self.send_request_repository = send_request_repository
        self.suppression_repository = suppression_repository

    def evaluate(self, db: Session, event: Event, decision: RuleDecision):
        """
        Returns:
        - ("allow", None)
        - ("alert", None)
        - ("suppress", reason)
        - ("none", None)
        """
        user_id = event.user_id
        if decision.action_type == "none":
            return "none", None

        # Internal alerts bypass suppression
        if decision.action_type == "alert":
            return "alert", None

        mode = decision.suppression_mode or "none"

        if mode == "none":
            return "allow", None

        if mode == "once_ever":
            exists = self.send_request_repository.exists_for_user_and_template(
                db=db,
                user_id=user_id,
                template_name=decision.template_name,
            )
            if exists:
                return "suppress", "once_ever"
            return "allow", None

        if mode == "once_per_calendar_day":
            exists_in_window = (
                self.send_request_repository.exists_for_user_and_template_in_day_so_far(
                    db=db,
                    user_id=user_id,
                    template_name=decision.template_name,
                    provided_ts=event.event_timestamp,
                )
            )

            if exists_in_window:
                return "suppress", "once_per_calendar_day"
            return "allow", None

        # Unknown suppression mode → fail open
        return "allow", None
