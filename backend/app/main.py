
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
