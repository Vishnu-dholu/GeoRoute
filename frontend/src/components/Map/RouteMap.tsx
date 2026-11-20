
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import type { Coordinate } from "../../services/routingService";

interface RouteMapProps {
  start: Coordinate | null;
  end: Coordinate | null;
  route: Coordinate[];
  onMapClick: (coordinate: Coordinate) => void;
}

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

export default function RouteMap({
  start,
  end,
  route,
  onMapClick,
}: RouteMapProps) {
  const center: Coordinate = [12.9716, 77.5946];

  return (
    <div className="h-[520px] w-full overflow-hidden rounded-xl border border-slate-700">
      <MapContainer
        center={center}
        zoom={13}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onMapClick={onMapClick} />

        {start && (
          <Marker position={start} icon={startIcon}>
            <Popup>Starting Location</Popup>
          </Marker>
        )}

        {end && (
          <Marker position={end} icon={endIcon}>
            <Popup>Destination</Popup>
          </Marker>
        )}

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
