from abc import ABC
from abc import abstractmethod


class IMessagingProvider(ABC):
    @abstractmethod
    def send_message(self, user_id: str, template_name: str, channel: str, reason: str) -> None:
        pass
