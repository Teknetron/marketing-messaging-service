from abc import ABC, abstractmethod

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
    def get_latest_by_user_and_type(self, db: Session, user_id: str, event_type: str) -> Event | None:
        raise NotImplementedError



class ISendRequestRepository(ABC):
    @abstractmethod
    def add(self, db: Session, send_request: SendRequest) -> SendRequest:
        raise NotImplementedError


class ISuppressionRepository(ABC):
    @abstractmethod
    def add(self, db: Session, suppression: Suppression) -> Suppression:
        raise NotImplementedError
