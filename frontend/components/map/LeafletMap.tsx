"use client";

import {
  Circle,
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMapEvents,
} from "react-leaflet";

export interface MapPoint {
  id: string;
  lat: number;
  lng: number;
  label: string;
  subtitle?: string | null;
  distanceMeters?: number | null;
}

interface LeafletMapProps {
  points: MapPoint[];
  centerLat: number;
  centerLng: number;
  zoom: number;
  heightClassName: string;
  selectable: boolean;
  selectedLocation: { lat: number; lng: number } | null;
  onSelectLocation?: (lat: number, lng: number) => void;
  radiusMeters?: number;
}

function MapClickCapture({
  enabled,
  onSelect,
}: {
  enabled: boolean;
  onSelect?: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click: (event) => {
      if (!enabled || !onSelect) return;
      onSelect(event.latlng.lat, event.latlng.lng);
    },
  });

  return null;
}

export default function LeafletMap({
  points,
  centerLat,
  centerLng,
  zoom,
  heightClassName,
  selectable,
  selectedLocation,
  onSelectLocation,
  radiusMeters,
}: LeafletMapProps) {
  return (
    <div
      className={`w-full overflow-hidden rounded-xl border border-gray-200 ${heightClassName}`}
    >
      <MapContainer
        center={[centerLat, centerLng]}
        zoom={zoom}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickCapture enabled={selectable} onSelect={onSelectLocation} />

        {radiusMeters && radiusMeters > 0 && (
          <Circle
            center={[centerLat, centerLng]}
            radius={radiusMeters}
            pathOptions={{ color: "#2563eb", opacity: 0.35, fillOpacity: 0.07 }}
          />
        )}

        {points.map((point) => (
          <CircleMarker
            key={point.id}
            center={[point.lat, point.lng]}
            radius={8}
            pathOptions={{
              color: "#1d4ed8",
              fillColor: "#2563eb",
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-gray-900">
                  {point.label}
                </p>
                {point.subtitle && (
                  <p className="text-xs text-gray-600">{point.subtitle}</p>
                )}
                {typeof point.distanceMeters === "number" && (
                  <p className="text-xs text-gray-500">
                    Aprox. {Math.round(point.distanceMeters)} m
                  </p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {selectedLocation && (
          <CircleMarker
            center={[selectedLocation.lat, selectedLocation.lng]}
            radius={10}
            pathOptions={{
              color: "#dc2626",
              fillColor: "#ef4444",
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <p className="text-sm font-semibold">Tu ubicación seleccionada</p>
              <p className="text-xs text-gray-600">
                {selectedLocation.lat.toFixed(5)},{" "}
                {selectedLocation.lng.toFixed(5)}
              </p>
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>
    </div>
  );
}
