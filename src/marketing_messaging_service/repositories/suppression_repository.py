from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.suppression import Suppression
from src.marketing_messaging_service.repositories.interfaces import ISuppressionRepository


class SuppressionRepository(ISuppressionRepository):
    def add(self, db: Session, suppression: Suppression) -> Suppression:
        db.add(suppression)
        db.flush()
        db.refresh(suppression)
        return suppression
