
import math

import networkx as nx
import osmnx as ox


EARTH_RADIUS_M = 6_371_000


def haversine_distance(node1, node2, G):
    """
    Calculate straight-line distance between two graph nodes.
    Returns distance in metres.
    """

    lat1 = math.radians(G.nodes[node1]["y"])
    lon1 = math.radians(G.nodes[node1]["x"])

    lat2 = math.radians(G.nodes[node2]["y"])
    lon2 = math.radians(G.nodes[node2]["x"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_M * math.asin(
        math.sqrt(min(1.0, a))
    )


def find_nearest_node(G, coordinates):
    """
    Find nearest road node.

    Input coordinates: [latitude, longitude]
    """

    lat, lon = coordinates

    return ox.distance.nearest_nodes(
        G,
        X=lon,
        Y=lat,
    )


def select_best_edge(G, u, v, weight):
    """
    Select minimum-weight parallel edge.
    """

    edges = G.get_edge_data(u, v)

    if not edges:
        raise ValueError(f"No edge found between {u} and {v}")

    key = min(
        edges,
        key=lambda k: float(
            edges[k].get(weight, math.inf)
        ),
    )

    return edges[key]


def get_edge_coordinates(G, u, v, edge_data):
    """
    Extract edge geometry as [latitude, longitude].
    """

    geometry = edge_data.get("geometry")

    if geometry is not None:
        coords = list(geometry.coords)
    else:
        coords = [
            (G.nodes[u]["x"], G.nodes[u]["y"]),
            (G.nodes[v]["x"], G.nodes[v]["y"]),
        ]

    u_point = (G.nodes[u]["x"], G.nodes[u]["y"])

    first = coords[0]
    last = coords[-1]

    first_distance = (
        (first[0] - u_point[0]) ** 2
        + (first[1] - u_point[1]) ** 2
    )

    last_distance = (
        (last[0] - u_point[0]) ** 2
        + (last[1] - u_point[1]) ** 2
    )

    if last_distance < first_distance:
        coords.reverse()

    return [(lat, lon) for lon, lat in coords]


def get_max_graph_speed(G):
    """
    Calculate maximum effective edge speed in metres/second.
    """

    max_speed = 0.0

    for _, _, _, data in G.edges(keys=True, data=True):

        length = float(data.get("length", 0))
        travel_time = float(data.get("travel_time", 0))

        if length > 0 and travel_time > 0:
            speed = length / travel_time
            max_speed = max(max_speed, speed)

    if max_speed <= 0:
        raise ValueError(
            "Could not determine a valid maximum graph speed"
        )

    return max_speed


def compute_route(
    G,
    start,
    end,
    criteria="distance",
    algorithm="dijkstra",
):
    """
    Compute optimal route using Dijkstra or A*.

    criteria:
        distance -> shortest distance
        time     -> fastest estimated time

    algorithm:
        dijkstra -> Dijkstra's shortest path
        astar    -> A* search
    """

    if criteria not in ("distance", "time"):
        raise ValueError("Invalid routing criteria")

    if algorithm not in ("dijkstra", "astar"):
        raise ValueError("Invalid routing algorithm")

    weight = (
        "length"
        if criteria == "distance"
        else "travel_time"
    )

    # Find nearest road nodes
    start_node = find_nearest_node(G, start)
    end_node = find_nearest_node(G, end)

    # Configure A* heuristic
    if algorithm == "astar":

        if criteria == "distance":

            def heuristic(u, v):
                return haversine_distance(u, v, G)

        else:

            max_speed = get_max_graph_speed(G)

            def heuristic(u, v):
                straight_distance = haversine_distance(
                    u, v, G
                )

                return straight_distance / max_speed

    else:
        heuristic = None

    # Execute shortest-path algorithm
    try:

        if algorithm == "dijkstra":

            path = nx.shortest_path(
                G,
                source=start_node,
                target=end_node,
                weight=weight,
                method="dijkstra",
            )

        else:

            path = nx.astar_path(
                G,
                source=start_node,
                target=end_node,
                heuristic=heuristic,
                weight=weight,
            )

    except nx.NetworkXNoPath:
        raise ValueError(
            "No route found between selected locations"
        )

    except nx.NodeNotFound:
        raise ValueError(
            "Selected road node does not exist"
        )

    # Reconstruct route geometry
    coordinates = []

    total_distance = 0.0
    total_time = 0.0

    for u, v in zip(path[:-1], path[1:]):

        edge_data = select_best_edge(
            G, u, v, weight
        )

        total_distance += float(
            edge_data.get("length", 0)
        )

        total_time += float(
            edge_data.get("travel_time", 0)
        )

        edge_coords = get_edge_coordinates(
            G, u, v, edge_data
        )

        if coordinates and edge_coords:
            edge_coords = edge_coords[1:]

        coordinates.extend(edge_coords)

    # Handle identical start and destination nodes
    if not coordinates:

        node = G.nodes[start_node]

        coordinates = [
            (node["y"], node["x"])
        ]

    return {
        "coordinates": coordinates,
        "distance_m": round(total_distance, 2),
        "travel_time_s": round(total_time, 2),

        "metadata": {
            "algorithm": algorithm,
            "criteria": criteria,
            "start_node": start_node,
            "end_node": end_node,
            "nodes_in_route": len(path),
        },
    }
