
import csv
import random
from pathlib import Path

import networkx as nx

from app.graph import load_road_graph
from app.benchmark import compare_algorithms
from app.routing import haversine_distance


# Experiment configuration
NUM_ROUTES = 5
REPETITIONS = 20
RANDOM_SEED = 42

CRITERIA = ["distance", "time"]

OUTPUT_DIR = Path("results")
OUTPUT_FILE = OUTPUT_DIR / "batch_benchmark.csv"


def select_route_pairs(G, count=NUM_ROUTES):
    """
    Select reproducible origin-destination pairs.

    All selected nodes belong to the largest strongly
    connected component, ensuring directed reachability.
    """

    if not G.is_directed():
        raise ValueError("Expected a directed road graph")

    components = list(nx.strongly_connected_components(G))

    if not components:
        raise ValueError("No strongly connected components found")

    largest_component = max(components, key=len)

    if len(largest_component) < 2:
        raise ValueError("Not enough connected road nodes")

    nodes = list(largest_component)

    rng = random.Random(RANDOM_SEED)

    # Generate candidate pairs
    candidates = set()

    target_candidates = min(2000, len(nodes) * (len(nodes) - 1) // 2)

    while len(candidates) < target_candidates:
        u, v = rng.sample(nodes, 2)

        # Canonical ordering prevents duplicate pairs
        candidates.add(tuple(sorted((u, v))))

    # Calculate straight-line separation
    ranked_pairs = []

    for u, v in candidates:
        distance = haversine_distance(u, v, G)
        ranked_pairs.append((distance, u, v))

    ranked_pairs.sort(key=lambda item: item[0])

    # Select pairs at different distance quantiles
    quantiles = [0.10, 0.30, 0.50, 0.70, 0.90]

    selected = []

    for quantile in quantiles[:count]:
        index = round(
            quantile * (len(ranked_pairs) - 1)
        )

        _, u, v = ranked_pairs[index]

        selected.append((u, v))

    return selected


def node_coordinates(G, node):
    """Return [latitude, longitude] for a graph node."""

    return [
        float(G.nodes[node]["y"]),
        float(G.nodes[node]["x"]),
    ]


def run_batch_benchmark(G):
    """Execute Dijkstra vs A* across multiple routes."""

    route_pairs = select_route_pairs(G)

    rows = []

    print("\n========== BATCH BENCHMARK ==========")
    print(f"Routes: {len(route_pairs)}")
    print(f"Repetitions: {REPETITIONS}")

    for route_index, (start_node, end_node) in enumerate(
        route_pairs, start=1
    ):

        start = node_coordinates(G, start_node)
        end = node_coordinates(G, end_node)

        print(f"\nRoute {route_index}")
        print(f"Start node: {start_node}")
        print(f"End node: {end_node}")

        for criteria in CRITERIA:

            result = compare_algorithms(
                G=G,
                start=start,
                end=end,
                criteria=criteria,
                repetitions=REPETITIONS,
            )

            if not result["comparison"]["optimality_verified"]:
                raise RuntimeError(
                    f"Optimality verification failed: "
                    f"Route {route_index}, {criteria}"
                )

            comparison = result["comparison"]

            for algorithm in ["dijkstra", "astar"]:

                metrics = result[algorithm]

                rows.append({
                    "route_id": route_index,
                    "start_node": start_node,
                    "end_node": end_node,
                    "criteria": criteria,
                    "algorithm": algorithm,
                    "execution_time_ms": metrics[
                        "execution_time_ms"
                    ],
                    "expanded_nodes": metrics[
                        "expanded_nodes"
                    ],
                    "settled_nodes": metrics[
                        "settled_nodes"
                    ],
                    "distance_m": metrics["distance_m"],
                    "travel_time_s": metrics["travel_time_s"],
                    "nodes_in_route": metrics["nodes_in_route"],
                    "objective_cost": metrics["objective_cost"],
                    "speedup": comparison["speedup"],
                    "execution_improvement_percent": comparison[
                        "execution_time_improvement_percent"
                    ],
                    "expanded_nodes_reduction_percent": comparison[
                        "expanded_nodes_reduction_percent"
                    ],
                    "optimality_verified": comparison[
                        "optimality_verified"
                    ],
                })

            print(
                f"  {criteria}: "
                f"Dijkstra={result['dijkstra']['execution_time_ms']:.4f} ms, "
                f"A*={result['astar']['execution_time_ms']:.4f} ms, "
                f"Speedup={comparison['speedup']}x"
            )

    return rows


def save_results(rows):
    """Save benchmark results as CSV."""

    if not rows:
        raise ValueError("No benchmark results to save")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV saved to: {OUTPUT_FILE.resolve()}")


def main():
    print("Loading road network...")

    G = load_road_graph()

    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")

    rows = run_batch_benchmark(G)

    save_results(rows)

    print("\n========== BENCHMARK COMPLETED ==========")
    print(f"Total benchmark records: {len(rows)}")
    print(f"Optimality checks passed: {len(rows)}")


if __name__ == "__main__":
    main()
