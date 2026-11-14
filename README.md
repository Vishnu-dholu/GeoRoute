# GeoRoute

A GIS-based multi-criteria route optimisation and analysis system for Bengaluru.

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Leaflet / React-Leaflet

### Backend

- Python
- FastAPI
- OSMnx
- NetworkX
- GeoPandas
- Shapely

## Core Features

- Interactive Bengaluru road map
- Start and destination selection
- Shortest-distance routing using Dijkstra
- Fastest-time routing using Dijkstra/A\*
- Route distance and estimated travel time
- Simulated road closures
- Alternative route calculation

## Project Structure

- `frontend/` - React application
- `backend/` - FastAPI application
- `docs/` - Technical documentation
- `report/` - Project report

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
# Activate virtual environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
