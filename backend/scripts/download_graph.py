
from pathlib import Path

import osmnx as ox


# ============================================================
# CONFIGURATION
# ============================================================

# Bengaluru study area
# OSMnx 2.x bounding box order:
# (west, south, east, north)

BBOX = (
    77.35,   # West
    12.75,   # South
    77.85,   # East
    13.20,   # North
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# New graph file (preserve Koramangala graph)
GRAPH_PATH = DATA_DIR / "bengaluru.graphml"


# ============================================================
# DOWNLOAD ROAD NETWORK
# ============================================================

def download_road_network():

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Enable OSMnx caching and logging
    ox.settings.use_cache = True
    ox.settings.log_console = True

    print("=" * 55)
    print("       GEOROUTE - BENGALURU ROAD NETWORK")
    print("=" * 55)

    print("\nStudy area:", BBOX)
    print("\nDownloading Bengaluru road network...")

    # --------------------------------------------------------
    # 1. Download driving road network
    # --------------------------------------------------------

    G = ox.graph_from_bbox(
        bbox=BBOX,
        network_type="drive",
        simplify=True,
    )

    if G.number_of_nodes() == 0:
        raise RuntimeError(
            "Downloaded graph contains no nodes."
        )

    print("\nRoad network downloaded successfully.")

    # --------------------------------------------------------
    # 2. Add road speed information
    # --------------------------------------------------------

    print("\nAdding road speed information...")

    G = ox.add_edge_speeds(G)

    # --------------------------------------------------------
    # 3. Calculate travel times
    # --------------------------------------------------------

    print("\nCalculating travel times...")

    G = ox.add_edge_travel_times(G)

    # --------------------------------------------------------
    # 4. Print graph statistics
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("ROAD NETWORK STATISTICS")
    print("=" * 55)

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
    print("Directed:", G.is_directed())
    print("Multigraph:", G.is_multigraph())
    print("CRS:", G.graph.get("crs"))

    # --------------------------------------------------------
    # 5. Save graph
    # --------------------------------------------------------

    print("\nSaving Bengaluru graph...")

    ox.save_graphml(
        G,
        filepath=GRAPH_PATH,
    )

    print("\nGraph saved successfully!")
    print("Location:", GRAPH_PATH)

    # --------------------------------------------------------
    # 6. Calculate geographic bounds
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("GEOGRAPHIC BOUNDS")
    print("=" * 55)

    xs = [
        data["x"]
        for _, data in G.nodes(data=True)
    ]

    ys = [
        data["y"]
        for _, data in G.nodes(data=True)
    ]

    print("North:", max(ys))
    print("South:", min(ys))
    print("East:", max(xs))
    print("West:", min(xs))

    # --------------------------------------------------------
    # 7. Display sample edge information
    # --------------------------------------------------------

    print("\n" + "=" * 55)
    print("SAMPLE ROAD EDGE")
    print("=" * 55)

    u, v, key, data = next(
        iter(G.edges(keys=True, data=True))
    )

    print("Source node:", u)
    print("Target node:", v)
    print("Edge key:", key)

    print(
        "Length:",
        data.get("length"),
        "metres"
    )

    print(
        "Speed:",
        data.get("speed_kph"),
        "km/h"
    )

    print(
        "Travel time:",
        data.get("travel_time"),
        "seconds"
    )

    # --------------------------------------------------------
    # 8. Final confirmation
    # --------------------------------------------------------

    file_size_mb = GRAPH_PATH.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 55)
    print("BENGALURU GRAPH GENERATION COMPLETED")
    print("=" * 55)

    print("Graph file:", GRAPH_PATH.name)
    print("File size:", round(file_size_mb, 2), "MB")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    download_road_network()
