
from typing import Literal

from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    start: tuple[float, float] = Field(
        ...,
        description="Starting coordinates [latitude, longitude]",
    )

    end: tuple[float, float] = Field(
        ...,
        description="Destination coordinates [latitude, longitude]",
    )

    criteria: Literal["distance", "time"] = Field(
        default="distance",
        description="Routing criteria",
    )


class RouteResponse(BaseModel):
    coordinates: list[tuple[float, float]]
    distance_m: float
    travel_time_s: float
    metadata: dict
