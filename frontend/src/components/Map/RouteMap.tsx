
import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import type { Coordinate } from "../../services/routingService";

interface RouteMapProps {
  start: Coordinate | null;
  end: Coordinate | null;
  route: Coordinate[];
  onMapClick: (coordinate: Coordinate) => void;
}

// Full Bengaluru study area from the backend graph.
const BENGALURU_BOUNDS: [[number, number], [number, number]] = [
  [12.7500008, 77.3500031], // Southwest
  [13.1999793, 77.849979],  // Northeast
];

const BENGALURU_CENTER: Coordinate = [12.975, 77.60];

// Starting location marker.
const startIcon = L.divIcon({
  className: "",
  html: `
    <div style="
      width: 18px;
      height: 18px;
      background: #3b82f6;
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 8px #0008;
    "></div>
  `,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

// Destination marker.
const endIcon = L.divIcon({
  className: "",
  html: `
    <div style="
      width: 18px;
      height: 18px;
      background: #a855f7;
      border: 3px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 8px #0008;
    "></div>
  `,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

// Handle map clicks.
function MapClickHandler({
  onMapClick,
}: {
  onMapClick: (coordinate: Coordinate) => void;
}) {
  useMapEvents({
    click(event) {
      onMapClick([event.latlng.lat, event.latlng.lng]);
    },
  });

  return null;
}

// Automatically adjust the viewport.
function MapViewportController({
  route,
}: {
  route: Coordinate[];
}) {
  const map = useMap();

  const routeKey = route
    .map(([lat, lon]) => `${lat},${lon}`)
    .join("|");

  useEffect(() => {
    // If a route exists, zoom into the complete route.
    if (route.length > 1) {
      const bounds = L.latLngBounds(route);

      map.fitBounds(bounds, {
        padding: [45, 45],
        maxZoom: 16,
        animate: true,
        duration: 0.8,
      });

      return;
    }

    // If there is no route, show the entire study area.
    map.fitBounds(BENGALURU_BOUNDS, {
      padding: [20, 20],
      maxZoom: 11,
      animate: true,
      duration: 0.8,
    });

  }, [map, routeKey]);

  return null;
}

export default function RouteMap({
  start,
  end,
  route,
  onMapClick,
}: RouteMapProps) {
  return (
    <div className="h-[520px] w-full overflow-hidden rounded-xl border border-slate-700">

      <MapContainer
        center={BENGALURU_CENTER}
        zoom={10}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onMapClick={onMapClick} />

        <MapViewportController route={route} />

        {/* Starting location */}
        {start && (
          <Marker position={start} icon={startIcon}>
            <Popup>Starting Location</Popup>
          </Marker>
        )}

        {/* Destination */}
        {end && (
          <Marker position={end} icon={endIcon}>
            <Popup>Destination</Popup>
          </Marker>
        )}

        {/* Calculated route */}
        {route.length > 1 && (
          <Polyline
            positions={route}
            pathOptions={{
              color: "#2563eb",
              weight: 6,
              opacity: 0.9,
            }}
          />
        )}

      </MapContainer>
    </div>
  );
}
