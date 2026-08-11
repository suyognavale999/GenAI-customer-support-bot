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

    app_TERMS = [
        "app",
        "kpi",
        "engagement",
        "datasource",
        "chart",
        "graph",
        "dashboard",
        "report",
        "filter",
        "drilldown",
        "import",
        "custom logic",
        "query builder",
        "artisan",
        "database",
        "user",
        "login",
        "wamp",
        "laravel",
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

        if not any(
            term in normalized
            for term in self.app_TERMS
        ):
            raise ApplicationException(
                message=(
                    "Please ask a question related to "
                    "the application."
                ),
                status_code=400,
                error_code="OUT_OF_SCOPE_QUESTION",
            )

        return normalized