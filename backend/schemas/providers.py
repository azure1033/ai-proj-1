"""Provider-related request/response schemas."""

from pydantic import BaseModel


class ProviderCreateRequest(BaseModel):
    id: str
    name: str
    provider_type: str  # "llm" | "embedding"
    base_url: str
    api_key: str = ""
    model_name: str


class ProviderUpdateRequest(BaseModel):
    name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None


class ProviderTestRequest(BaseModel):
    api_key: str | None = None


class ProviderTestCustomRequest(BaseModel):
    base_url: str
    model_name: str
    api_key: str = ""

