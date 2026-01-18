from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.marketing_messaging_service.repositories.interfaces import (
    ISendRequestRepository,
    ISuppressionRepository,
)
from src.marketing_messaging_service.services.rule_models import RuleDecision


class SuppressionService:
    def __init__(
        self,
        send_request_repository: ISendRequestRepository,
        suppression_repository: ISuppressionRepository,
    ):
        self.send_request_repository = send_request_repository
        self.suppression_repository = suppression_repository

    def evaluate(self, db: Session, user_id: str, decision: RuleDecision):
        """
        Returns:
        - ("allow", None)
        - ("alert", None)
        - ("suppress", reason)
        - ("none", None)
        """

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
            today = datetime.now(timezone.utc).date()
            exists_today = self.send_request_repository.exists_for_user_and_template_on_date(
                db=db,
                user_id=user_id,
                template_name=decision.template_name,
                date=today,
            )
            if exists_today:
                return "suppress", "once_per_calendar_day"
            return "allow", None

        # Unknown suppression mode → fail open
        return "allow", None
