from fastapi import APIRouter
from sqlalchemy import func
from sqlalchemy import select

from app.api.dependencies import (
    AdminUserDependency,
    DatabaseDependency,
)
from app.models.conversation import Conversation
from app.models.feedback import Feedback
from app.models.message import Message


router = APIRouter(
    prefix="/admin/metrics",
    tags=["Monitoring"],
)


@router.get("")
def get_metrics(
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
):
    conversations = database.scalar(
        select(func.count(Conversation.id))
    )

    messages = database.scalar(
        select(func.count(Message.id))
    )

    positive_feedback = database.scalar(
        select(func.count(Feedback.id)).where(
            Feedback.rating == 1
        )
    )

    negative_feedback = database.scalar(
        select(func.count(Feedback.id)).where(
            Feedback.rating == -1
        )
    )

    return {
        "conversations": conversations or 0,
        "messages": messages or 0,
        "positive_feedback": positive_feedback or 0,
        "negative_feedback": negative_feedback or 0,
    }