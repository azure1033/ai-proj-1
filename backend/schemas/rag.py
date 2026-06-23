"""RAG-related request/response schemas."""

from pydantic import BaseModel


class RagSettingsRequest(BaseModel):
    embedding_model: str = "text2vec-base-chinese"
    device: str = "cpu"
    chunk_size: int = 384
    chunk_overlap: int = 64
    retrieval_k: int = 4
    load_strategy: str = "lazy"

