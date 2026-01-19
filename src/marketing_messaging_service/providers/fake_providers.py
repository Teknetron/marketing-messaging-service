from pathlib import Path
from typing import Dict, List

from .interfaces import IMessagingProvider


class FakeMessagingProvider(IMessagingProvider):
    """
    Simple provider that:
    - Stores sent messages in memory (for tests)
    - Appends each message to messages.txt (for debugging / audit)
    """

    # Minimal template catalog: template_name -> message text.
    # (These template names come from config/rules.yaml)
    _TEMPLATE_TEXT: dict[str, str] = {
        "WELCOME_EMAIL": "Welcome aboard! We're so excited to have you with us.",
        "BANK_LINK_SUCCESS_EMAIL": "You've just linked your bank account? Then you're almost ready to pay your rent!",
        "INSUFFICIENT_FUNDS_EMAIL": "It looks like your payment didn't go through due to a low balance. Just a quick top-up should do the trick!",
        "HIGH_RISK_ALERT": "We've noticed a few unsuccessful payment attempts and want to make sure your account is secure.",
    }
    def __init__(self, log_file: str = "messages.txt"):
        self.sent_messages: List[Dict[str, str]] = []
        self.log_path = Path(log_file)
        self.log_path.touch(exist_ok=True)

    def _render_text(self, template_name: str) -> str:
        return self._TEMPLATE_TEXT.get(template_name, f"[Missing template text for {template_name}]")

    def send_message(self, user_id: str, template_name: str, channel: str, reason: str) -> None:
        message_text = self._render_text(template_name)

        record = {
            "user_id": user_id,
            "template_name": template_name,
            "channel": channel,
            "reason": reason,
            "text": message_text,
        }

        self.sent_messages.append(record)

        # Persist to file
        line = (
            f"user_id={user_id} | template={template_name} | channel={channel} "
            f"| text={message_text} | reason={reason}\n"
        )
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line)

        print(f"[FAKE_PROVIDER] Sent message: {record} (logged to {self.log_path})")
