from app.core.config import settings
from app.rag.chunking import TextChunker
from app.rag.llm_service import LLMService
from app.rag.vector_store import VectorStore


class RAGService:

    def __init__(self):
        self.chunker = TextChunker()
        self.vector_store = VectorStore()

    def index_document(self, document):
        chunks = self.chunker.split(
            document.extracted_text
        )

        chunk_count = (
            self.vector_store.add_document(
                document_id=document.id,
                document_name=document.original_name,
                chunks=chunks,
            )
        )

        return chunk_count

    def delete_document(self, document_id):
        self.vector_store.delete_document(
            document_id
        )

    def answer(self, question):
        matches = self.vector_store.search(
            question=question,
            limit=settings.rag_top_k,
        )

        if not matches:
            return {
                "answer": (
                    "The uploaded documents do not contain "
                    "enough information to answer this question."
                ),
                "sources": [],
            }

        context_parts = []
        sources = []

        for index, match in enumerate(
            matches,
            start=1,
        ):
            metadata = match["metadata"]

            context_parts.append(
                "[Source "
                + str(index)
                + "]\n"
                + match["content"]
            )

            sources.append(
                {
                    "document_id": (
                        metadata["document_id"]
                    ),
                    "document_name": (
                        metadata["document_name"]
                    ),
                    "chunk_index": (
                        metadata["chunk_index"]
                    ),
                    "similarity": (
                        match["similarity"]
                    ),
                }
            )

        context = "\n\n".join(
            context_parts
        )

        llm_service = LLMService()

        answer = llm_service.generate_answer(
            question=question,
            context=context,
        )

        return {
            "answer": answer,
            "sources": sources,
        }