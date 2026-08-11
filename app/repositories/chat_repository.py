import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.feedback import Feedback
from app.models.message import Message


class ChatRepository:

    def __init__(self, database: Session):
        self.database = database

    def get_conversation(self, session_id):
        statement = select(Conversation).where(
            Conversation.session_id == session_id
        )

        return self.database.scalar(statement)

    def create_conversation(self, session_id, title):
        conversation = Conversation(
            session_id=session_id,
            title=title,
        )

        self.database.add(conversation)
        self.database.commit()
        self.database.refresh(conversation)

        return conversation

    def create_message(
        self,
        conversation_id,
        role,
        content,
        sources=None,
    ):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources_json=json.dumps(sources or []),
        )

        self.database.add(message)
        self.database.commit()
        self.database.refresh(message)

        return message

    def get_messages(self, conversation_id):
        statement = (
            select(Message)
            .where(
                Message.conversation_id
                == conversation_id
            )
            .order_by(Message.created_at.asc())
        )

        return list(
            self.database.scalars(statement).all()
        )

    def get_message(self, message_id):
        return self.database.get(
            Message,
            message_id,
        )

    def save_feedback(
        self,
        message_id,
        rating,
        comment,
    ):
        feedback = Feedback(
            message_id=message_id,
            rating=rating,
            comment=comment,
        )

        self.database.add(feedback)
        self.database.commit()
        self.database.refresh(feedback)

        return feedback
