from sqlalchemy import select
from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.suppression import Suppression
from src.marketing_messaging_service.repositories.interfaces import \
    ISuppressionRepository


class SuppressionRepository(ISuppressionRepository):
    def add(self, db: Session, suppression: Suppression) -> Suppression:
        db.add(suppression)
        db.flush()
        db.refresh(suppression)
        return suppression

    def list_by_user(self, db: Session, user_id: str) -> list[Suppression]:
        stmt = (
            select(Suppression)
            .where(Suppression.user_id == user_id)
            .order_by(Suppression.decided_at.desc())
        )
        return list(db.scalars(stmt).all())
