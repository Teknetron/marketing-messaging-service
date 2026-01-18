from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.orm import Session

from src.marketing_messaging_service.models.event import Event
from src.marketing_messaging_service.models.send_request import SendRequest
from src.marketing_messaging_service.models.suppression import Suppression


class IEventRepository(ABC):
    @abstractmethod
    def add(self, db: Session, event: Event) -> Event:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, db: Session, event_id: int) -> Event | None:
        raise NotImplementedError

    @abstractmethod
    def get_latest_by_user_and_type(
        self, db: Session, user_id: str, event_type: str
    ) -> Event | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, db: Session, user_id: str) -> list[Event]:
        raise NotImplementedError

    @abstractmethod
    def exists_by_user_and_type_in_window(
        self,
        db: Session,
        user_id: str,
        event_type: str,
        window_start: datetime,
        window_end: datetime,
    ) -> bool:
        raise NotImplementedError


class ISendRequestRepository(ABC):
    @abstractmethod
    def add(self, db: Session, send_request: SendRequest) -> SendRequest:
        raise NotImplementedError

    def exists_for_user_and_template(self, db, user_id: str, template_name: str) -> bool:
        raise NotImplementedError

    def exists_for_user_and_template_on_date(
        self, db, user_id: str, template_name: str, date
    ) -> bool:
        raise NotImplementedError


class ISuppressionRepository(ABC):
    @abstractmethod
    def add(self, db: Session, suppression: Suppression) -> Suppression:
        raise NotImplementedError
