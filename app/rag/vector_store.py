import chromadb

from app.core.config import settings
from app.core.exceptions import ApplicationException


class VectorStore:

    def __init__(self):
        settings.chroma_persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(
                settings.chroma_persist_directory
            )
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={
                    "hnsw:space": "cosine"
                },
            )
        )

    def add_document(
        self,
        document_id,
        document_name,
        chunks,
    ):
        if not chunks:
            raise ApplicationException(
                message="No text chunks were generated.",
                status_code=400,
                error_code="NO_DOCUMENT_CHUNKS",
            )

        self.delete_document(document_id)

        chunk_ids = []
        metadata_list = []

        for index, chunk in enumerate(chunks):
            chunk_id = (
                f"document-{document_id}-chunk-{index}"
            )

            chunk_metadata = {
                "document_id": document_id,
                "document_name": document_name,
                "chunk_index": index,
            }

            chunk_ids.append(chunk_id)
            metadata_list.append(chunk_metadata)

        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadata_list,
        )

        return len(chunk_ids)

    def search(self, question, limit):
        collection_count = self.collection.count()

        if collection_count == 0:
            return []

        result = self.collection.query(
            query_texts=[question],
            n_results=min(
                limit,
                collection_count,
            ),
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        documents = result.get(
            "documents",
            [[]],
        )[0]

        metadata_list = result.get(
            "metadatas",
            [[]],
        )[0]

        distances = result.get(
            "distances",
            [[]],
        )[0]

        matches = []

        for document, metadata, distance in zip(
            documents,
            metadata_list,
            distances,
        ):
            similarity = 1.0 - float(distance)

            if similarity < settings.rag_min_similarity:
                continue

            matches.append(
                {
                    "content": document,
                    "metadata": metadata,
                    "similarity": round(
                        similarity,
                        4,
                    ),
                }
            )

        return matches

    def delete_document(self, document_id):
        self.collection.delete(
            where={
                "document_id": document_id
            }
        )

    def count(self):
        return self.collection.count()