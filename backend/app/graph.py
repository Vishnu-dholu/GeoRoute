
from pathlib import Path

import osmnx as ox
import networkx as nx


BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_PATH = BASE_DIR / "data" / "koramangala.graphml"


def load_road_graph() -> nx.MultiDiGraph:
    """Load the saved OSM road network."""

    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Road network not found: {GRAPH_PATH}. "
            "Run scripts/download_graph.py first."
        )

    G = ox.load_graphml(filepath=GRAPH_PATH)

    print("Road network loaded successfully")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")

    return G


def get_graph_statistics(G: nx.MultiDiGraph) -> dict:
    """Return basic road network statistics."""

    nodes = G.number_of_nodes()
    edges = G.number_of_edges()

    xs = [data["x"] for _, data in G.nodes(data=True)]
    ys = [data["y"] for _, data in G.nodes(data=True)]

    return {
        "nodes": nodes,
        "edges": edges,
        "directed": G.is_directed(),
        "multigraph": G.is_multigraph(),
        "crs": G.graph.get("crs"),
        "bounds": {
            "north": max(ys),
            "south": min(ys),
            "east": max(xs),
            "west": min(xs),
        },
    }
