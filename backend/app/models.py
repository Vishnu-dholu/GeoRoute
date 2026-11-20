
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

    algorithm: Literal["dijkstra", "astar"] = Field(
        default="dijkstra",
        description="Pathfinding algorithm",
    )


class RouteResponse(BaseModel):
    coordinates: list[tuple[float, float]]
    distance_m: float
    travel_time_s: float
    metadata: dict


class BenchmarkRequest(BaseModel):
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

    repetitions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of benchmark repetitions",
    )


class BenchmarkAlgorithmResult(BaseModel):
    execution_time_ms: float
    expanded_nodes: int
    settled_nodes: int
    distance_m: float
    travel_time_s: float
    nodes_in_route: int
    objective_cost: float


class BenchmarkComparison(BaseModel):
    execution_time_improvement_percent: float
    expanded_nodes_reduction_percent: float
    speedup: float | None
    optimality_verified: bool


class BenchmarkResponse(BaseModel):
    criteria: Literal["distance", "time"]
    repetitions: int
    start_node: int
    end_node: int

    dijkstra: BenchmarkAlgorithmResult
    astar: BenchmarkAlgorithmResult

    comparison: BenchmarkComparison
