from sqlalchemy import select
from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.decision import Decision
from src.marketing_messaging_service.repositories.interfaces import \
    IDecisionRepository


class DecisionRepository(IDecisionRepository):
    def add(self, db: Session, decision: Decision) -> Decision:
        db.add(decision)
        db.flush()
        db.refresh(decision)
        return decision

    def list_by_user(self, db: Session, user_id: str) -> list[Decision]:
        stmt = (
            select(Decision)
            .where(Decision.user_id == user_id)
            .order_by(Decision.created_at.desc())
        )
        return list(db.scalars(stmt).all())
