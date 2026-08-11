import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import ApplicationException
from app.rag.rag_service import RAGService
from app.repositories.chat_repository import ChatRepository
from app.core.guardrails import ChatGuardrail


class ChatService:

    def __init__(self, database: Session):
        self.repository = ChatRepository(database)
        self.rag_service = RAGService()
        self.guardrail = ChatGuardrail()


    def ask(self, question, session_id=None):
        self.guardrail.validate(question)
        current_session_id = (
            session_id or uuid4().hex
        )

        conversation = (
            self.repository.get_conversation(
                current_session_id
            )
        )

        if conversation is None:
            conversation = (
                self.repository.create_conversation(
                    session_id=current_session_id,
                    title=question[:100],
                )
            )

        self.repository.create_message(
            conversation_id=conversation.id,
            role="user",
            content=question,
        )

        result = self.rag_service.answer(question)

        assistant_message = (
            self.repository.create_message(
                conversation_id=conversation.id,
                role="assistant",
                content=result["answer"],
                sources=result["sources"],
            )
        )

        return {
            "session_id": current_session_id,
            "message_id": assistant_message.id,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    def get_history(self, session_id):
        conversation = (
            self.repository.get_conversation(
                session_id
            )
        )

        if conversation is None:
            raise ApplicationException(
                message="Conversation not found.",
                status_code=404,
                error_code="CONVERSATION_NOT_FOUND",
            )

        messages = self.repository.get_messages(
            conversation.id
        )

        history = []

        for message in messages:
            sources = []

            if message.sources_json:
                try:
                    sources = json.loads(
                        message.sources_json
                    )
                except json.JSONDecodeError:
                    sources = []

            history.append(
                {
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "sources": sources,
                    "created_at": (
                        message.created_at.isoformat()
                    ),
                }
            )

        return history

    def submit_feedback(
        self,
        message_id,
        rating,
        comment=None,
    ):
        message = self.repository.get_message(
            message_id
        )

        if message is None:
            raise ApplicationException(
                message="Message not found.",
                status_code=404,
                error_code="MESSAGE_NOT_FOUND",
            )

        if message.role != "assistant":
            raise ApplicationException(
                message=(
                    "Feedback can only be submitted "
                    "for assistant messages."
                ),
                status_code=400,
                error_code="INVALID_FEEDBACK_MESSAGE",
            )

        return self.repository.save_feedback(
            message_id=message_id,
            rating=rating,
            comment=comment,
        )