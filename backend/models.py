"""External place models; intentionally independent of priced sample hotels."""
from pydantic import BaseModel, Field


class ExternalHotel(BaseModel):
    provider: str = "geoapify"
    place_id: str
    name: str | None = None
    address: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    distance_meters: float = Field(ge=0)
