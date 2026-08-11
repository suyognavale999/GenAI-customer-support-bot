from fastapi import APIRouter

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)