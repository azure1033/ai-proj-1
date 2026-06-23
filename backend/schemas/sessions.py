"""Session-related request/response schemas."""

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    name: str | None = None


class UpdateSessionRequest(BaseModel):
    name: str


class SessionResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    message_count: int
    preview: str


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]

