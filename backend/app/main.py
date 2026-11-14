from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GeoRoute API",
    description="GIS-based multi-criteria route optimisation system",
    version="1.0.0",
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