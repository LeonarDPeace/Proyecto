"use client";

/**
 * MapView — Componente de mapa interactivo del campus.
 *
 * Renderiza puntos y opcionalmente permite seleccionar coordenadas.
 */

import dynamic from "next/dynamic";

import type { MapPoint } from "@/components/map/LeafletMap";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-96 w-full items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 text-sm text-gray-500">
      Cargando mapa interactivo...
    </div>
  ),
});

interface MapViewProps {
  points?: MapPoint[];
  centerLat?: number;
  centerLng?: number;
  zoom?: number;
  heightClassName?: string;
  selectable?: boolean;
  selectedLocation?: { lat: number; lng: number } | null;
  onSelectLocation?: (lat: number, lng: number) => void;
  radiusMeters?: number;
}

export default function MapView({
  points = [],
  centerLat,
  centerLng,
  zoom = 16,
  heightClassName = "h-96",
  selectable = false,
  selectedLocation = null,
  onSelectLocation,
  radiusMeters,
}: MapViewProps) {
  const defaultLat = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || "3.3516");
  const defaultLng = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LNG || "-76.5320");

  return (
    <LeafletMap
      points={points}
      centerLat={centerLat ?? defaultLat}
      centerLng={centerLng ?? defaultLng}
      zoom={zoom}
      heightClassName={heightClassName}
      selectable={selectable}
      selectedLocation={selectedLocation}
      onSelectLocation={onSelectLocation}
      radiusMeters={radiusMeters}
    />
  );
}
