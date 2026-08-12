import re

from app.core.exceptions import ApplicationException


class ChatGuardrail:

    BLOCKED_PATTERNS = [
        r"ignore previous instructions",
        r"reveal.*system prompt",
        r"show.*api key",
        r"show.*password",
        r"developer message",
    ]

    def validate(self, question):
        normalized = " ".join(
            question.lower().split()
        )

        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, normalized):
                raise ApplicationException(
                    message="Unsafe request detected.",
                    status_code=400,
                    error_code="UNSAFE_CHAT_REQUEST",
                )

        return normalized