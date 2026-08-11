from fastapi import APIRouter

from app.api.dependencies import (
    AdminUserDependency,
    DatabaseDependency,
)
from app.core.exceptions import ApplicationException
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.rag.rag_service import RAGService
from app.schemas.rag import (
    IndexDocumentResponse,
    RAGAnswerResponse,
    RAGQuestionRequest,
)


router = APIRouter(
    prefix="/admin/rag",
    tags=["RAG"],
)


@router.post(
    "/documents/{document_id}/index",
    response_model=IndexDocumentResponse,
)
def index_document(
    document_id: int,
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
):
    repository = DocumentRepository(database)

    document = repository.get_by_id(document_id)

    if document is None:
        raise ApplicationException(
            message="Document not found.",
            status_code=404,
            error_code="DOCUMENT_NOT_FOUND",
        )

    chunks_created = RAGService().index_document(
        document
    )

    document.status = "indexed"
    document.chroma_document_id = str(document.id)

    database.commit()
    database.refresh(document)

    return IndexDocumentResponse(
        message="Document indexed successfully.",
        chunks_created=chunks_created,
    )


@router.post(
    "/ask",
    response_model=RAGAnswerResponse,
)
def ask_question(
    request: RAGQuestionRequest,
    admin_user: AdminUserDependency,
):
    result = RAGService().answer(
        request.question
    )

    return RAGAnswerResponse(**result)