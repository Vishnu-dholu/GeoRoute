
from pathlib import Path

import osmnx as ox
import networkx as nx


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load the expanded Bengaluru road network
GRAPH_PATH = BASE_DIR / "data" / "bengaluru.graphml"


# ============================================================
# LOAD ROAD NETWORK
# ============================================================

def load_road_graph() -> nx.MultiDiGraph:
    """Load the saved Bengaluru OSM road network."""

    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Road network not found: {GRAPH_PATH}. "
            "Run scripts/download_graph.py first."
        )

    print("\nLoading Bengaluru road network...")

    G = ox.load_graphml(filepath=GRAPH_PATH)

    if G.number_of_nodes() == 0:
        raise RuntimeError(
            "Loaded road network contains no nodes."
        )

    if G.number_of_edges() == 0:
        raise RuntimeError(
            "Loaded road network contains no edges."
        )

    print("\nRoad network loaded successfully!")

    print("Graph file:", GRAPH_PATH.name)
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Directed:", G.is_directed())
    print("Multigraph:", G.is_multigraph())
    print("CRS:", G.graph.get("crs"))

    return G


# ============================================================
# GRAPH STATISTICS
# ============================================================

def get_graph_statistics(G: nx.MultiDiGraph) -> dict:
    """Return basic road network statistics."""

    nodes = G.number_of_nodes()
    edges = G.number_of_edges()

    if nodes == 0:
        raise ValueError("Graph contains no nodes")

    xs = [
        data["x"]
        for _, data in G.nodes(data=True)
    ]

    ys = [
        data["y"]
        for _, data in G.nodes(data=True)
    ]

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
