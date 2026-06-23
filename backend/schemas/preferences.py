"""Preference-related request schemas."""

from pydantic import BaseModel


class PreferencesRequest(BaseModel):
    session_id: str
    key: str
    value: str

