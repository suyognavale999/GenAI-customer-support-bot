from fastapi import APIRouter

from app.api.dependencies import DatabaseDependency
from app.schemas.chat import ChatRequest
from app.schemas.chat import ChatResponse
from app.schemas.chat import FeedbackRequest
from app.schemas.chat import FeedbackResponse
from app.schemas.chat import MessageResponse
from app.services.chat_service import ChatService

from fastapi import Request

from app.core.config import settings
from app.core.rate_limit import limiter


router = APIRouter(
    prefix="/chat",
    tags=["Customer Support Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
@limiter.limit(settings.chat_rate_limit)
def ask_question(
    request: Request,
    chat_request: ChatRequest,
    database: DatabaseDependency,
):
    result = ChatService(database).ask(
        question=chat_request.question,
        session_id=chat_request.session_id,
    )

    return ChatResponse(**result)


@router.get(
    "/history/{session_id}",
    response_model=list[MessageResponse],
)
def get_chat_history(
    session_id: str,
    database: DatabaseDependency,
):
    history = ChatService(
        database
    ).get_history(session_id)

    return history


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
)
def submit_feedback(
    request: FeedbackRequest,
    database: DatabaseDependency,
):
    ChatService(database).submit_feedback(
        message_id=request.message_id,
        rating=request.rating,
        comment=request.comment,
    )

    return FeedbackResponse(
        message="Feedback submitted successfully."
    )