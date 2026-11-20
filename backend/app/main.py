
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import RouteRequest, RouteResponse
from app.routing import compute_route

from app.models import BenchmarkRequest, BenchmarkResponse
from app.benchmark import compare_algorithms

from app.graph import load_road_graph, get_graph_statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the road network once at startup
    app.state.road_graph = load_road_graph()

    yield

    # Cleanup when application shuts down
    app.state.road_graph = None


app = FastAPI(
    title="GeoRoute API",
    description="GIS-based multi-criteria route optimisation system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to GeoRoute API",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/graph_stats")
def graph_stats(request: Request):
    G = request.app.state.road_graph

    return get_graph_statistics(G)


@app.post("/api/route", response_model=RouteResponse)
def calculate_route(req: RouteRequest, request: Request):

    G = request.app.state.road_graph

    print("\n========== ROUTE API DEBUG ==========")
    print("Received algorithm:", req.algorithm)
    print("Received criteria:", req.criteria)

    try:
        result = compute_route(
            G=G,
            start=req.start,
            end=req.end,
            criteria=req.criteria,
            algorithm=req.algorithm,
        )

        print("Returned algorithm:", result["metadata"]["algorithm"])
        print("=====================================\n")

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )



@app.post(
    "/api/benchmark",
    response_model=BenchmarkResponse,
)
def benchmark_route(
    req: BenchmarkRequest,
    request: Request,
):
    G = request.app.state.road_graph

    try:
        result = compare_algorithms(
            G=G,
            start=req.start,
            end=req.end,
            criteria=req.criteria,
            repetitions=req.repetitions,
        )

        if not result["comparison"]["optimality_verified"]:
            raise HTTPException(
                status_code=500,
                detail="Dijkstra and A* returned different optimal costs",
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
