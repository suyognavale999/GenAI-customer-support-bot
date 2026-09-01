from fastapi import APIRouter

from app.api.dependencies import (
    AdminUserDependency,
    DatabaseDependency,
)
from app.services.document_service import DocumentService


router = APIRouter(
    # prefix="/rag"
    prefix="/admin/rag",
    tags=["RAG"],
)


@router.post("/documents/{document_id}/index")
def index_document(
    document_id: int,
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
):
    document_service = DocumentService(database)

    chunks_created = document_service.index_document(
        document_id
    )

    return {
        "message": "Document indexed successfully.",
        "document_id": document_id,
        "chunks_created": chunks_created,
    }