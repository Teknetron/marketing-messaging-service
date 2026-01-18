from typing import List, Dict

from .interfaces import IMessagingProvider


class FakeMessagingProvider(IMessagingProvider):
    """
    Very simple provider that stores sent messages in memory for:
    - debugging via logs
    - deterministic tests
    """
    def __init__(self):
        self.sent_messages: List[Dict[str, str]] = []

    def send_message(self, user_id: str, template_name: str, channel: str, reason: str) -> None:
        record = {
            "user_id": user_id,
            "template_name": template_name,
            "channel": channel,
            "reason": reason,
        }
        self.sent_messages.append(record)
        print(f"[FAKE_PROVIDER] Sent message: {record}")
