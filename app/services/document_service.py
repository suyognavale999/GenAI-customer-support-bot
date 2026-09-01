import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.rag.rag_service import RAGService

from app.core.config import settings
from app.core.exceptions import ApplicationException
from app.models.knowledge_document import KnowledgeDocument
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.services.text_extraction_service import (
    TextExtractionService,
)

import logging
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024

class DocumentService:
    def __init__(self, database: Session):
        self.repository = DocumentRepository(database)
        self.text_extractor = TextExtractionService()

    async def upload(self, uploaded_file: UploadFile):
        if not uploaded_file.filename:
            raise ApplicationException(
                message="A filename is required.",
                status_code=400,
                error_code="MISSING_FILENAME",
            )

        original_name = Path(uploaded_file.filename).name

        file_content = await uploaded_file.read()

        if not file_content:
            await uploaded_file.close()

            raise ApplicationException(
                message="The uploaded file is empty.",
                status_code=400,
                error_code="EMPTY_FILE",
            )

        if len(file_content) > MAX_FILE_SIZE:
            await uploaded_file.close()

            raise ApplicationException(
                message="Maximum allowed file size is 10 MB.",
                status_code=413,
                error_code="FILE_TOO_LARGE",
            )

        checksum = hashlib.sha256(file_content).hexdigest()

        existing_document = self.repository.get_by_checksum(checksum)

        if existing_document:
            await uploaded_file.close()

            raise ApplicationException(
                message=("This document has already been uploaded."),
                status_code=409,
                error_code="DUPLICATE_DOCUMENT",
            )

        extracted_text = self.text_extractor.extract_text(
            original_name,
            file_content,
        )

        extension = Path(original_name).suffix.lower()

        stored_name = f"{uuid4().hex}{extension}"

        settings.upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = settings.upload_directory / stored_name

        try:
            file_path.write_bytes(file_content)

            document = KnowledgeDocument(
                original_name=original_name,
                stored_name=stored_name,
                content_type=(uploaded_file.content_type or "application/octet-stream"),
                file_size=len(file_content),
                checksum=checksum,
                extracted_text=extracted_text,
                status="ready",
            )

            saved_document = self.repository.create(document)
            
            logger.info(
                "Indexing document id=%s, extracted_chars=%s",
                saved_document.id,
                len(saved_document.extracted_text),
            )
            
            RAGService().index_document(saved_document)
            return saved_document

        except Exception:
            file_path.unlink(missing_ok=True)
            raise

        finally:
            await uploaded_file.close()
            
    def index_document(self, document_id: int):
        document = self.repository.get_by_id(document_id)

        if document is None:
            raise ApplicationException(
                message="Document not found.",
                status_code=404,
                error_code="DOCUMENT_NOT_FOUND",
            )

        if not document.extracted_text:
            raise ApplicationException(
                message="Document contains no extracted text.",
                status_code=400,
                error_code="EMPTY_DOCUMENT_TEXT",
            )

        return RAGService().index_document(document)

    def list_documents(self):
        return self.repository.get_all()

    def delete_document(self, document_id: int):
        document = self.repository.get_by_id(document_id)

        if document is None:
            raise ApplicationException(
                message="Document not found.",
                status_code=404,
                error_code="DOCUMENT_NOT_FOUND",
            )

        file_path = settings.upload_directory / document.stored_name

        RAGService().delete_document(document.id)

        self.repository.delete(document)

        file_path.unlink(missing_ok=True)
