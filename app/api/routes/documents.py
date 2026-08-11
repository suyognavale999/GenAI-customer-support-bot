from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile

from app.api.dependencies import (
    AdminUserDependency,
)
from app.api.dependencies import (
    DatabaseDependency,
)
from app.schemas.document import (
    DocumentDeleteResponse,
)
from app.schemas.document import (
    DocumentResponse,
)
from app.schemas.document import (
    DocumentUploadResponse,
)
from app.services.document_service import (
    DocumentService,
)


router = APIRouter(
    prefix="/admin/documents",
    tags=["Knowledge Base"],
)


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=201,
)
async def upload_document(
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
    file: UploadFile = File(...),
):
    document_service = DocumentService(
        database
    )

    document = await document_service.upload(
        file
    )

    document_response = (
        DocumentResponse.model_validate(
            document
        )
    )

    return DocumentUploadResponse(
        message="Document uploaded successfully.",
        document=document_response,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
):
    document_service = DocumentService(
        database
    )

    documents = (
        document_service.list_documents()
    )

    response = []

    for document in documents:
        response.append(
            DocumentResponse.model_validate(
                document
            )
        )

    return response


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
)
def delete_document(
    document_id: int,
    database: DatabaseDependency,
    admin_user: AdminUserDependency,
):
    document_service = DocumentService(
        database
    )

    document_service.delete_document(
        document_id
    )

    return DocumentDeleteResponse(
        message="Document deleted successfully."
    )