from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument


class DocumentRepository:

    def __init__(self, database: Session):
        self.database = database

    def get_by_checksum(self, checksum: str):
        statement = select(KnowledgeDocument).where(
            KnowledgeDocument.checksum == checksum
        )

        return self.database.scalar(statement)

    def get_by_id(self, document_id: int):
        document = self.database.get(
            KnowledgeDocument,
            document_id
        )

        return document

    def get_all(self):
        statement = select(KnowledgeDocument).order_by(
            KnowledgeDocument.created_at.desc()
        )

        result = self.database.scalars(statement)
        documents = result.all()

        return documents

    def create(self, document: KnowledgeDocument):
        self.database.add(document)
        self.database.commit()
        self.database.refresh(document)

        return document

    def delete(self, document: KnowledgeDocument):
        self.database.delete(document)
        self.database.commit()