from pydantic import BaseModel
from pydantic import Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )

    session_id: str | None = Field(
        default=None,
        max_length=100,
    )


class SourceResponse(BaseModel):
    document_id: int
    document_name: str
    chunk_index: int
    similarity: float


class ChatResponse(BaseModel):
    session_id: str
    message_id: int
    answer: str
    sources: list[SourceResponse]


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: list
    created_at: str


class FeedbackRequest(BaseModel):
    message_id: int
    rating: int = Field(
        ge=-1,
        le=1,
    )

    comment: str | None = Field(
        default=None,
        max_length=500,
    )


class FeedbackResponse(BaseModel):
    message: str