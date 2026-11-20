
import heapq
import itertools
import math
import statistics
import time

from app.routing import (
    find_nearest_node,
    get_max_graph_speed,
    haversine_distance,
    select_best_edge,
)


def run_instrumented_search(
    G,
    start_node,
    end_node,
    weight,
    algorithm,
    heuristic=None,
):
    """
    Run Dijkstra or A* while tracking explored nodes.

    Returns:
        path
        expanded_nodes
        settled_nodes
        execution_time_ms
    """

    if algorithm not in ("dijkstra", "astar"):
        raise ValueError("Invalid algorithm")

    if start_node == end_node:
        return [start_node], 0, 1, 0.0

    counter = itertools.count()

    distances = {start_node: 0.0}
    previous = {}

    # (priority, actual_cost, tie_breaker, node)
    queue = [
        (0.0, 0.0, next(counter), start_node)
    ]

    expanded_nodes = 0
    settled_nodes = 0

    start_time = time.perf_counter()

    while queue:

        priority, current_cost, _, u = heapq.heappop(queue)

        # Ignore outdated queue entries
        if current_cost > distances.get(u, math.inf):
            continue

        settled_nodes += 1

        # Destination reached
        if u == end_node:
            execution_time_ms = (
                time.perf_counter() - start_time
            ) * 1000

            path = []
            current = end_node

            while current is not None:
                path.append(current)
                current = previous.get(current)

            path.reverse()

            return (
                path,
                expanded_nodes,
                settled_nodes,
                execution_time_ms,
            )

        expanded_nodes += 1

        # Examine outgoing edges
        for _, v, key, data in G.out_edges(
            u, keys=True, data=True
        ):

            edge_cost = float(data.get(weight, math.inf))

            if not math.isfinite(edge_cost) or edge_cost < 0:
                continue

            new_cost = current_cost + edge_cost

            if new_cost < distances.get(v, math.inf):

                distances[v] = new_cost
                previous[v] = u

                h = (
                    heuristic(v, end_node)
                    if algorithm == "astar"
                    else 0.0
                )

                heapq.heappush(
                    queue,
                    (
                        new_cost + h,
                        new_cost,
                        next(counter),
                        v,
                    ),
                )

    raise ValueError("No route found between selected locations")


def calculate_path_metrics(G, path, weight):
    """
    Calculate distance and travel time for a path.
    """

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

    return {
        "distance_m": round(total_distance, 2),
        "travel_time_s": round(total_time, 2),
        "nodes_in_route": len(path),
    }



def benchmark_algorithm(
    G,
    start_node,
    end_node,
    criteria,
    algorithm,
    repetitions=5,
):
    """
    Benchmark one algorithm using warm-up and median metrics.
    """

    weight = (
        "length"
        if criteria == "distance"
        else "travel_time"
    )

    # Configure heuristic outside the timed search
    if algorithm == "astar":

        if criteria == "distance":

            def heuristic(u, v):
                return haversine_distance(u, v, G)

        else:

            max_speed = get_max_graph_speed(G)

            def heuristic(u, v):
                return (
                    haversine_distance(u, v, G)
                    / max_speed
                )

    else:
        heuristic = None

    # ----------------------------------
    # 1. Warm-up run (not measured)
    # ----------------------------------

    run_instrumented_search(
        G=G,
        start_node=start_node,
        end_node=end_node,
        weight=weight,
        algorithm=algorithm,
        heuristic=heuristic,
    )

    # ----------------------------------
    # 2. Collect measured repetitions
    # ----------------------------------

    execution_times = []
    expanded_counts = []
    settled_counts = []

    path = None

    for _ in range(repetitions):

        (
            current_path,
            expanded,
            settled,
            elapsed,
        ) = run_instrumented_search(
            G=G,
            start_node=start_node,
            end_node=end_node,
            weight=weight,
            algorithm=algorithm,
            heuristic=heuristic,
        )

        path = current_path

        execution_times.append(elapsed)
        expanded_counts.append(expanded)
        settled_counts.append(settled)

    # ----------------------------------
    # 3. Calculate median metrics
    # ----------------------------------

    median_execution_time = statistics.median(
        execution_times
    )

    median_expanded_nodes = statistics.median(
        expanded_counts
    )

    median_settled_nodes = statistics.median(
        settled_counts
    )

    # ----------------------------------
    # 4. Calculate route metrics
    # ----------------------------------

    metrics = calculate_path_metrics(
        G, path, weight
    )

    objective_cost = (
        metrics["distance_m"]
        if criteria == "distance"
        else metrics["travel_time_s"]
    )

    # ----------------------------------
    # 5. Return benchmark results
    # ----------------------------------

    return {
        "execution_time_ms": round(
            median_execution_time, 4
        ),
        "expanded_nodes": round(
            median_expanded_nodes
        ),
        "settled_nodes": round(
            median_settled_nodes
        ),
        "distance_m": metrics["distance_m"],
        "travel_time_s": metrics["travel_time_s"],
        "nodes_in_route": metrics["nodes_in_route"],
        "objective_cost": objective_cost,
    }


def compare_algorithms(
    G,
    start,
    end,
    criteria="distance",
    repetitions=5,
):
    """
    Compare Dijkstra and A* on the same road network.
    """

    if criteria not in ("distance", "time"):
        raise ValueError("Invalid routing criteria")

    if not 1 <= repetitions <= 20:
        raise ValueError("Repetitions must be between 1 and 20")

    start_node = find_nearest_node(G, start)
    end_node = find_nearest_node(G, end)

    dijkstra = benchmark_algorithm(
        G,
        start_node,
        end_node,
        criteria,
        "dijkstra",
        repetitions,
    )

    astar = benchmark_algorithm(
        G,
        start_node,
        end_node,
        criteria,
        "astar",
        repetitions,
    )

    # Verify both algorithms found the same optimal cost
    dijkstra_cost = dijkstra["objective_cost"]
    astar_cost = astar["objective_cost"]

    optimality_verified = math.isclose(
        dijkstra_cost,
        astar_cost,
        rel_tol=1e-7,
        abs_tol=1e-6,
    )

    dijkstra_time = dijkstra["execution_time_ms"]
    astar_time = astar["execution_time_ms"]

    dijkstra_nodes = dijkstra["expanded_nodes"]
    astar_nodes = astar["expanded_nodes"]

    time_improvement = (
        (dijkstra_time - astar_time) / dijkstra_time * 100
        if dijkstra_time > 0 else 0.0
    )

    node_reduction = (
        (dijkstra_nodes - astar_nodes) / dijkstra_nodes * 100
        if dijkstra_nodes > 0 else 0.0
    )

    return {
        "criteria": criteria,
        "repetitions": repetitions,
        "start_node": start_node,
        "end_node": end_node,
        "dijkstra": dijkstra,
        "astar": astar,
        "comparison": {
            "execution_time_improvement_percent": round(
                time_improvement, 2
            ),
            "expanded_nodes_reduction_percent": round(
                node_reduction, 2
            ),
            "speedup": round(
                dijkstra_time / astar_time, 3
            ) if astar_time > 0 else None,
            "optimality_verified": optimality_verified,
        },
    }
