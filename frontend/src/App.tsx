
import { useState } from "react";

import RouteMap from "./components/Map/RouteMap";
import {
  calculateRoute,
  type Coordinate,
  type RouteResponse,
  type Algorithm,
} from "./services/routingService";

type Criteria = "distance" | "time";

interface AlgorithmResult {
  execution_time_ms: number;
  expanded_nodes: number;
  settled_nodes: number;
  distance_m: number;
  travel_time_s: number;
  nodes_in_route: number;
  objective_cost: number;
}

interface BenchmarkResult {
  criteria: Criteria;
  repetitions: number;
  start_node: number;
  end_node: number;
  dijkstra: AlgorithmResult;
  astar: AlgorithmResult;
  comparison: {
    execution_time_improvement_percent: number;
    expanded_nodes_reduction_percent: number;
    speedup: number | null;
    optimality_verified: boolean;
  };
}

const API_URL = "http://localhost:8000";

const inputClass =
  "mt-2 w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-3 text-sm text-white outline-none transition focus:border-blue-500 focus:ring-1 focus:ring-blue-500";

const cardClass =
  "rounded-xl border border-slate-800 bg-slate-900 p-5 sm:p-6";

function App() {
  const [startLat, setStartLat] = useState("12.9352");
  const [startLon, setStartLon] = useState("77.6245");
  const [endLat, setEndLat] = useState("12.9400");
  const [endLon, setEndLon] = useState("77.6100");

  const [criteria, setCriteria] = useState<Criteria>("distance");
  const [repetitions, setRepetitions] = useState(5);

  const [result, setResult] = useState<BenchmarkResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [algorithm, setAlgorithm] = useState<Algorithm>("astar");

  const [routeResult, setRouteResult] = useState<RouteResponse | null>(null);

  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState("");

  const [selectionMode, setSelectionMode] = useState<"start" | "end">("start");

  const format = (value: number) =>
    value.toLocaleString("en-IN", { maximumFractionDigits: 2 });

  const runRoute = async () => {
  setRouteError("");
  setRouteResult(null);

  const values = [startLat, startLon, endLat, endLon];

  if (values.some((value) => !value.trim())) {
    setRouteError("Please enter all coordinates.");
    return;
  }

  const [lat1, lon1, lat2, lon2] = values.map(Number);

  if (
    ![lat1, lon1, lat2, lon2].every(Number.isFinite) ||
    Math.abs(lat1) > 90 ||
    Math.abs(lat2) > 90 ||
    Math.abs(lon1) > 180 ||
    Math.abs(lon2) > 180
  ) {
    setRouteError("Please enter valid latitude and longitude values.");
    return;
  }

  setRouteLoading(true);

  try {
    const data = await calculateRoute({
      start: [lat1, lon1],
      end: [lat2, lon2],
      criteria,
      algorithm,
    });

    setRouteResult(data);
  } catch (err) {
    setRouteError(
      err instanceof Error
        ? err.message
        : "Unable to calculate the route."
    );
  } finally {
    setRouteLoading(false);
  }
};

  const runBenchmark = async () => {
    setError("");
    setResult(null);

    const values = [startLat, startLon, endLat, endLon];

    if (values.some((v) => !v.trim())) {
      setError("Please enter all coordinates.");
      return;
    }

    const [lat1, lon1, lat2, lon2] = values.map(Number);

    if (
      ![lat1, lon1, lat2, lon2].every(Number.isFinite) ||
      Math.abs(lat1) > 90 ||
      Math.abs(lat2) > 90 ||
      Math.abs(lon1) > 180 ||
      Math.abs(lon2) > 180
    ) {
      setError("Please enter valid latitude and longitude values.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/benchmark`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start: [lat1, lon1],
          end: [lat2, lon2],
          criteria,
          repetitions,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Benchmark request failed."
        );
      }

      setResult(data as BenchmarkResult);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to GeoRoute backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleMapClick = (coordinate: Coordinate) => {
  const [latitude, longitude] = coordinate;

  if (selectionMode === "start") {
    setStartLat(latitude.toFixed(6));
    setStartLon(longitude.toFixed(6));
    setSelectionMode("end");
  } else {
    setEndLat(latitude.toFixed(6));
    setEndLon(longitude.toFixed(6));
    setSelectionMode("start");
  }

  setRouteResult(null);
  setRouteError("");
};

  return (
    <div className="min-h-screen bg-[#090e19] text-slate-200">
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold">
              G
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">GeoRoute</h1>
              <p className="text-[9px] tracking-[2px] text-slate-500">
                GIS ROUTING & ANALYTICS
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span className="h-2 w-2 rounded-full bg-green-400" />
            <span>Performance Lab</span>
            <span className="rounded-md bg-slate-800 px-2 py-1">v1.0</span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-7 px-5 py-9 sm:px-8">
        {/* Page heading */}
        <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <p className="mb-2 text-[10px] font-bold tracking-[2px] text-blue-400">
              ROUTING ANALYSIS / BENCHMARK
            </p>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Algorithm Performance
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Compare Dijkstra and A* on the Bengaluru road network.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs text-green-400">
            <span className="h-2 w-2 rounded-full bg-green-400" />
            Road network available
          </div>
        </section>


        {/* Interactive Route Planner */}
        <section className={cardClass}>
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-[10px] font-bold tracking-widest text-blue-400">
                INTERACTIVE GIS
              </p>
              <h3 className="mt-1 text-xl font-bold">Route Planner</h3>
              <p className="mt-1 text-xs text-slate-500">
                Select locations on the map and calculate the optimal route.
              </p>
            </div>

            <span className="rounded-md bg-blue-500/10 px-3 py-2 text-xs text-blue-400">
              Bengaluru Road Network
            </span>
          </div>

          <div className="mb-4 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setSelectionMode("start")}
              className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                selectionMode === "start"
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 text-slate-400 hover:bg-slate-800"
              }`}
            >
              Select Starting Point
            </button>

            <button
              onClick={() => setSelectionMode("end")}
              className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                selectionMode === "end"
                  ? "bg-purple-600 text-white"
                  : "border border-slate-700 text-slate-400 hover:bg-slate-800"
              }`}
            >
              Select Destination
            </button>

            <span className="text-xs text-slate-500">
              Click the map to set the{" "}
              <strong className="text-white">
                {selectionMode === "start" ? "starting point" : "destination"}
              </strong>
            </span>
          </div>

          <RouteMap
            start={
              Number.isFinite(Number(startLat)) &&
              Number.isFinite(Number(startLon)) &&
              Math.abs(Number(startLat)) <= 90 &&
              Math.abs(Number(startLon)) <= 180
                ? [Number(startLat), Number(startLon)]
                : null
            }
            end={
              Number.isFinite(Number(endLat)) &&
              Number.isFinite(Number(endLon)) &&
              Math.abs(Number(endLat)) <= 90 &&
              Math.abs(Number(endLon)) <= 180
                ? [Number(endLat), Number(endLon)]
                : null
            }
            route={routeResult?.coordinates ?? []}
            onMapClick={handleMapClick}
          />

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div>
              <label className="text-xs text-slate-400">
                Route Optimization
              </label>
              <select
                value={criteria}
                onChange={(e) => {
                  setCriteria(e.target.value as Criteria);
                  setRouteResult(null);
                }}
                className={inputClass}
              >
                <option value="distance">Shortest Distance</option>
                <option value="time">Fastest Travel Time</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-400">
                Routing Algorithm
              </label>
              <select
                value={algorithm}
                onChange={(e) => {
                  setAlgorithm(e.target.value as Algorithm);
                  setRouteResult(null);
                }}
                className={inputClass}
              >
                <option value="astar">A* Search</option>
                <option value="dijkstra">Dijkstra</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={runRoute}
                disabled={routeLoading}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-wait disabled:opacity-60"
              >
                {routeLoading ? "Calculating Route..." : "Calculate Route"}
              </button>
            </div>
          </div>

          {routeError && (
            <div className="mt-4 rounded-lg border border-red-900 bg-red-950/50 p-3 text-sm text-red-300">
              {routeError}
            </div>
          )}

          {routeResult && (
            <div className="mt-5 rounded-xl border border-blue-900 bg-blue-950/30 p-5">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                <h4 className="font-semibold text-white">Route Calculated</h4>
                <span className="rounded-md bg-blue-500/10 px-3 py-1 text-xs text-blue-400">
                  {routeResult.metadata.algorithm.toUpperCase()}
                </span>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div>
                  <p className="text-xs text-slate-400">Distance</p>
                  <p className="mt-2 text-xl font-bold text-white">
                    {format(routeResult.distance_m / 1000)} km
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-400">Estimated Travel Time</p>
                  <p className="mt-2 text-xl font-bold text-white">
                    {format(routeResult.travel_time_s / 60)} min
                  </p>
                </div>

                <div>
                  <p className="text-xs text-slate-400">Route Nodes</p>
                  <p className="mt-2 text-xl font-bold text-white">
                    {routeResult.metadata.nodes_in_route}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>


        {/* Configuration */}
        <section className={cardClass}>
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Benchmark Configuration</h3>
              <p className="mt-1 text-xs text-slate-500">
                Configure your route and optimization parameters.
              </p>
            </div>
            <span className="text-[10px] tracking-widest text-slate-500">
              01 / CONFIGURE
            </span>
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            <CoordinateInput
              title="Starting Location"
              color="bg-blue-400"
              latitude={startLat}
              longitude={startLon}
              setLatitude={setStartLat}
              setLongitude={setStartLon}
            />

            <CoordinateInput
              title="Destination"
              color="bg-purple-400"
              latitude={endLat}
              longitude={endLon}
              setLatitude={setEndLat}
              setLongitude={setEndLon}
            />
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div>
              <label className="text-xs text-slate-400">
                Optimization Criteria
              </label>
              <select
                value={criteria}
                onChange={(e) => setCriteria(e.target.value as Criteria)}
                className={inputClass}
              >
                <option value="distance">Shortest Distance</option>
                <option value="time">Fastest Travel Time</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-400">
                Benchmark Repetitions
              </label>
              <select
                value={repetitions}
                onChange={(e) => setRepetitions(Number(e.target.value))}
                className={inputClass}
              >
                {[1, 5, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>
                    {n} {n === 1 ? "Run" : "Runs"}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={runBenchmark}
                disabled={loading}
                className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-wait disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Running Benchmark...
                  </>
                ) : (
                  <>▶ Run Benchmark</>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-5 rounded-lg border border-red-900 bg-red-950/50 p-3 text-sm text-red-300">
              {error}
            </div>
          )}
        </section>

        {/* Empty state */}
        {!result && !loading && (
          <section className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 px-5 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-2xl text-blue-400">
              ↗
            </div>
            <h3 className="mt-4 font-semibold">Ready to Analyze</h3>
            <p className="mt-2 max-w-md text-xs leading-6 text-slate-500">
              Configure your route and run a benchmark to compare the
              performance of Dijkstra and A* algorithms.
            </p>
          </section>
        )}

        {loading && (
          <section className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900">
            <span className="h-9 w-9 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />
            <h3 className="mt-5 font-semibold">Analyzing Road Network</h3>
            <p className="mt-2 text-xs text-slate-500">
              Running algorithms and collecting performance metrics...
            </p>
          </section>
        )}

        {/* Results */}
        {result && (
          <>
            <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <p className="text-[10px] font-bold tracking-widest text-blue-400">
                  BENCHMARK RESULTS
                </p>
                <h3 className="mt-1 text-2xl font-bold">
                  Performance Overview
                </h3>
              </div>

              <span
                className={`w-fit rounded-lg border px-3 py-2 text-xs ${
                  result.comparison.optimality_verified
                    ? "border-green-900 bg-green-950/50 text-green-400"
                    : "border-red-900 bg-red-950/50 text-red-400"
                }`}
              >
                {result.comparison.optimality_verified
                  ? "✓ Optimality Verified"
                  : "! Optimality Mismatch"}
              </span>
            </section>

            {/* Summary cards */}
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                title="Execution Speedup"
                value={
                  result.comparison.speedup !== null
                    ? `${format(result.comparison.speedup)}×`
                    : "N/A"
                }
                detail="Dijkstra / A*"
                icon="⚡"
              />

              <StatCard
                title="Time Improvement"
                value={`${format(result.comparison.execution_time_improvement_percent)}%`}
                detail="Execution time difference"
                icon="◷"
              />

              <StatCard
                title="Node Reduction"
                value={`${format(result.comparison.expanded_nodes_reduction_percent)}%`}
                detail="Fewer expanded nodes"
                icon="◎"
              />

              <StatCard
                title="Route Distance"
                value={`${format(result.dijkstra.distance_m)} m`}
                detail="Calculated route distance"
                icon="↗"
              />
            </section>

            {/* Charts */}
            <section className="grid gap-5 lg:grid-cols-2">
              <ComparisonCard
                title="Execution Time"
                subtitle="Median execution time across repetitions"
                unit="MILLISECONDS"
                firstValue={result.dijkstra.execution_time_ms}
                secondValue={result.astar.execution_time_ms}
                format={format}
              />

              <ComparisonCard
                title="Expanded Nodes"
                subtitle="Nodes explored during graph traversal"
                unit="NODES"
                firstValue={result.dijkstra.expanded_nodes}
                secondValue={result.astar.expanded_nodes}
                format={format}
              />
            </section>

            {/* Comparison table */}
            <section className={cardClass}>
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold">
                    Detailed Algorithm Comparison
                  </h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Performance metrics from the benchmark API.
                  </p>
                </div>
                <span className="text-[10px] tracking-widest text-slate-500">
                  {result.repetitions} REPETITIONS
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[480px] text-left text-xs">
                  <thead className="text-[10px] uppercase tracking-wider text-slate-500">
                    <tr className="border-b border-slate-700">
                      <th className="px-4 py-4">Metric</th>
                      <th className="px-4 py-4">Dijkstra</th>
                      <th className="px-4 py-4">A*</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      ["Execution Time", `${format(result.dijkstra.execution_time_ms)} ms`, `${format(result.astar.execution_time_ms)} ms`],
                      ["Expanded Nodes", format(result.dijkstra.expanded_nodes), format(result.astar.expanded_nodes)],
                      ["Settled Nodes", format(result.dijkstra.settled_nodes), format(result.astar.settled_nodes)],
                      ["Route Distance", `${format(result.dijkstra.distance_m)} m`, `${format(result.astar.distance_m)} m`],
                      ["Travel Time", `${format(result.dijkstra.travel_time_s)} s`, `${format(result.astar.travel_time_s)} s`],
                      ["Nodes in Route", format(result.dijkstra.nodes_in_route), format(result.astar.nodes_in_route)],
                      ["Objective Cost", format(result.dijkstra.objective_cost), format(result.astar.objective_cost)],
                    ].map(([label, dijkstra, astar]) => (
                      <tr
                        key={label}
                        className="border-b border-slate-800 last:border-0 hover:bg-slate-800/30"
                      >
                        <td className="px-4 py-4 text-slate-400">{label}</td>
                        <td className="px-4 py-4 tabular-nums">{dijkstra}</td>
                        <td className="px-4 py-4 font-semibold text-purple-300 tabular-nums">
                          {astar}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Route information */}
            <section className={cardClass}>
              <h3 className="font-semibold">Route Information</h3>
              <p className="mt-1 text-xs text-slate-500">
                Selected road network nodes.
              </p>

              <div className="my-7 grid gap-5 text-center sm:grid-cols-3 sm:items-center">
                <div>
                  <p className="text-[10px] tracking-widest text-slate-500">
                    START NODE
                  </p>
                  <p className="mt-2 break-all text-sm font-semibold">
                    {result.start_node}
                  </p>
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="h-0.5 flex-1 bg-blue-500" />
                    <span className="text-xs text-slate-400">
                      {result.dijkstra.nodes_in_route} route nodes
                    </span>
                    <span className="h-0.5 flex-1 bg-purple-500" />
                  </div>
                </div>

                <div>
                  <p className="text-[10px] tracking-widest text-slate-500">
                    END NODE
                  </p>
                  <p className="mt-2 break-all text-sm font-semibold">
                    {result.end_node}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-green-900 bg-green-950/40 p-4">
                <p className="text-sm font-semibold text-green-400">
                  {result.comparison.optimality_verified
                    ? "✓ Optimality Check Passed"
                    : "! Optimality Check Failed"}
                </p>
                <p className="mt-1 text-xs text-green-300/70">
                  {result.comparison.optimality_verified
                    ? "Both algorithms returned the same objective cost."
                    : "The algorithms returned different objective costs."}
                </p>
              </div>
            </section>
          </>
        )}

        <footer className="flex flex-col justify-between gap-3 border-t border-slate-800 py-6 text-[10px] text-slate-500 sm:flex-row">
          <span className="font-semibold text-slate-300">GeoRoute</span>
          <span>GIS-Based Multi-Criteria Route Optimisation System</span>
        </footer>
      </main>
    </div>
  );
}

function CoordinateInput({
  title,
  color,
  latitude,
  longitude,
  setLatitude,
  setLongitude,
}: {
  title: string;
  color: string;
  latitude: string;
  longitude: string;
  setLatitude: (v: string) => void;
  setLongitude: (v: string) => void;
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
      <div className="mb-4 flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
        <h4 className="text-sm font-semibold">{title}</h4>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <label className="text-xs text-slate-400">
          Latitude
          <input
            type="number"
            step="any"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            className={inputClass}
          />
        </label>

        <label className="text-xs text-slate-400">
          Longitude
          <input
            type="number"
            step="any"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            className={inputClass}
          />
        </label>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  detail,
  icon,
}: {
  title: string;
  value: string;
  detail: string;
  icon: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400">{title}</span>
        <span className="text-xl text-blue-400">{icon}</span>
      </div>
      <p className="mt-5 text-2xl font-bold tracking-tight text-white">
        {value}
      </p>
      <p className="mt-2 text-[10px] text-slate-500">{detail}</p>
    </div>
  );
}

function ComparisonCard({
  title,
  subtitle,
  unit,
  firstValue,
  secondValue,
  format,
}: {
  title: string;
  subtitle: string;
  unit: string;
  firstValue: number;
  secondValue: number;
  format: (v: number) => string;
}) {
  const max = Math.max(firstValue, secondValue, 0.001);

  return (
    <section className={cardClass}>
      <div className="mb-7 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">{title}</h3>
          <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
        </div>
        <span className="text-[9px] tracking-widest text-slate-500">
          {unit}
        </span>
      </div>

      <div className="space-y-7">
        {[
          { label: "Dijkstra", value: firstValue, color: "bg-blue-500" },
          { label: "A*", value: secondValue, color: "bg-purple-500" },
        ].map((item) => (
          <div key={item.label}>
            <div className="mb-2 flex justify-between text-xs">
              <span className="text-slate-400">{item.label}</span>
              <strong className="tabular-nums text-white">
                {format(item.value)}
              </strong>
            </div>

            <div className="h-2.5 overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full transition-all duration-700 ${item.color}`}
                style={{ width: `${(item.value / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default App;
