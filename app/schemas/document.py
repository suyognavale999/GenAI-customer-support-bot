from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    content_type: str
    file_size: int
    status: str
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse


class DocumentDeleteResponse(BaseModel):
    message: str