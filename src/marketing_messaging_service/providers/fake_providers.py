from typing import List, Dict
from pathlib import Path

from .interfaces import IMessagingProvider


class FakeMessagingProvider(IMessagingProvider):
    """
    Simple provider that:
    - Stores sent messages in memory (for tests)
    - Appends each message to messages.txt (for debugging / audit)
    """
    def __init__(self, log_file: str = "messages.txt"):
        self.sent_messages: List[Dict[str, str]] = []
        self.log_path = Path(log_file)
        # Ensure file exists
        self.log_path.touch(exist_ok=True)

    def send_message(self, user_id: str, template_name: str, channel: str, reason: str) -> None:
        record = {
            "user_id": user_id,
            "template_name": template_name,
            "channel": channel,
            "reason": reason,
        }

        self.sent_messages.append(record)

        # Persist to file
        line = (
            f"user_id={user_id} | template={template_name} | channel={channel} "
            f"| reason={reason}\n"
        )
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line)

        print(f"[FAKE_PROVIDER] Sent message: {record} (logged to {self.log_path})")
