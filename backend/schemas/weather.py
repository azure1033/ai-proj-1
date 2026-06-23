"""Weather-related request schemas."""

from pydantic import BaseModel


class WeatherRequest(BaseModel):
    city: str | None = None
    query: str | None = None

