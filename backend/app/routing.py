
import math

import networkx as nx
import osmnx as ox


def find_nearest_node(G, coordinates):
    """
    Find nearest road-network node.

    API coordinates: [latitude, longitude]
    OSMnx expects: X=longitude, Y=latitude
    """
    lat, lon = coordinates

    return ox.distance.nearest_nodes(
        G,
        X=lon,
        Y=lat,
    )


def select_best_edge(G, u, v, weight):
    """
    Select the minimum-weight parallel edge
    between nodes u and v.
    """

    edges = G.get_edge_data(u, v)

    if not edges:
        raise ValueError(f"No edge found between {u} and {v}")

    key = min(
        edges,
        key=lambda k: float(edges[k].get(weight, math.inf)),
    )

    return edges[key]


def get_edge_coordinates(G, u, v, edge_data):
    """
    Extract edge geometry in [latitude, longitude] format.
    """

    geometry = edge_data.get("geometry")

    if geometry is not None:
        coords = list(geometry.coords)
    else:
        # Fallback: straight line between graph nodes
        coords = [
            (G.nodes[u]["x"], G.nodes[u]["y"]),
            (G.nodes[v]["x"], G.nodes[v]["y"]),
        ]

    # Ensure geometry follows u -> v direction
    u_point = (G.nodes[u]["x"], G.nodes[u]["y"])
    v_point = (G.nodes[v]["x"], G.nodes[v]["y"])

    first = coords[0]
    last = coords[-1]

    start_distance = (
        (first[0] - u_point[0]) ** 2
        + (first[1] - u_point[1]) ** 2
    )

    reverse_distance = (
        (last[0] - u_point[0]) ** 2
        + (last[1] - u_point[1]) ** 2
    )

    if reverse_distance < start_distance:
        coords.reverse()

    return [(lat, lon) for lon, lat in coords]


def compute_route(G, start, end, criteria="distance"):
    """
    Compute an optimal route using Dijkstra's algorithm.

    criteria:
        distance -> minimum distance
        time     -> minimum estimated travel time
    """

    if criteria not in ("distance", "time"):
        raise ValueError("Criteria must be 'distance' or 'time'")

    weight = "length" if criteria == "distance" else "travel_time"

    # Step 1: Find nearest graph nodes
    start_node = find_nearest_node(G, start)
    end_node = find_nearest_node(G, end)

    # Step 2: Run Dijkstra's algorithm
    try:
        path = nx.shortest_path(
            G,
            source=start_node,
            target=end_node,
            weight=weight,
            method="dijkstra",
        )
    except nx.NetworkXNoPath:
        raise ValueError("No route found between selected locations")

    # Step 3: Reconstruct route geometry and calculate totals
    coordinates = []

    total_distance = 0.0
    total_time = 0.0

    for u, v in zip(path[:-1], path[1:]):

        edge_data = select_best_edge(G, u, v, weight)

        total_distance += float(edge_data.get("length", 0))
        total_time += float(edge_data.get("travel_time", 0))

        edge_coords = get_edge_coordinates(
            G, u, v, edge_data
        )

        # Avoid duplicate consecutive coordinates
        if coordinates and edge_coords:
            edge_coords = edge_coords[1:]

        coordinates.extend(edge_coords)

    # Handle start and end being the same graph node
    if not coordinates:
        node = G.nodes[start_node]
        coordinates = [(node["y"], node["x"])]

    # Step 4: Return route information
    return {
        "coordinates": coordinates,
        "distance_m": round(total_distance, 2),
        "travel_time_s": round(total_time, 2),
        "metadata": {
            "algorithm": "Dijkstra",
            "criteria": criteria,
            "start_node": start_node,
            "end_node": end_node,
            "nodes_in_route": len(path),
        },
    }
