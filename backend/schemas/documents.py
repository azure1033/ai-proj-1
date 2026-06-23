"""Document-related response schemas."""

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    chunks: int = 0
    indexed: bool = False


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    chunks: int = 0
    indexed: bool = False

