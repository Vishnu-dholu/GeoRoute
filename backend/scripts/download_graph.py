
from pathlib import Path

import osmnx as ox
import networkx as nx


# Study area: Koramangala, Bengaluru
# Bounding box: north, south, east, west
BBOX = (77.6000, 12.9100, 77.6600, 12.9700)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GRAPH_PATH = DATA_DIR / "koramangala.graphml"


def download_road_network():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ox.settings.use_cache = True
    ox.settings.log_console = True

    print("Downloading Koramangala road network...")

    # Download roads within the specified bounding box
    G = ox.graph_from_bbox(
        bbox=BBOX,
        network_type="drive",
        simplify=True,
    )

    print("Adding road speed information...")
    G = ox.add_edge_speeds(G)

    print("Calculating travel times...")
    G = ox.add_edge_travel_times(G)

    print("\n--- Road Network Statistics ---")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Directed:", G.is_directed())
    print("Multigraph:", G.is_multigraph())

    print("\n--- Sample Edge ---")
    u, v, key, data = next(iter(G.edges(keys=True, data=True)))

    print("Source:", u)
    print("Target:", v)
    print("Edge key:", key)
    print("Length:", data.get("length"), "metres")
    print("Speed:", data.get("speed_kph"), "km/h")
    print("Travel time:", data.get("travel_time"), "seconds")

    ox.save_graphml(G, filepath=GRAPH_PATH)

    print("\nGraph saved successfully!")
    print("Location:", GRAPH_PATH)


if __name__ == "__main__":
    download_road_network()
