
const API_URL = "http://localhost:8000";

export type Coordinate = [number, number];
export type Criteria = "distance" | "time";
export type Algorithm = "dijkstra" | "astar";

export interface RouteRequest {
  start: Coordinate;
  end: Coordinate;
  criteria: Criteria;
  algorithm: Algorithm;
}

export interface RouteResponse {
  coordinates: Coordinate[];
  distance_m: number;
  travel_time_s: number;
  metadata: {
    algorithm: Algorithm;
    criteria: Criteria;
    start_node: number;
    end_node: number;
    nodes_in_route: number;
  };
}

export async function calculateRoute(
  request: RouteRequest
): Promise<RouteResponse> {
  const response = await fetch(`${API_URL}/api/route`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      error?.detail || `Route request failed: ${response.status}`
    );
  }

  return response.json() as Promise<RouteResponse>;
}
