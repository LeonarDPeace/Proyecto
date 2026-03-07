"use client";

/**
 * MapView — Componente de mapa interactivo del campus.
 *
 * Usa Leaflet + OpenStreetMap. Requiere 'use client' por interactividad.
 * Sprint 0: Placeholder. Sprint 1: Implementación con react-leaflet.
 */
export default function MapView() {
  const defaultLat = parseFloat(
    process.env.NEXT_PUBLIC_DEFAULT_LAT || "3.3516"
  );
  const defaultLng = parseFloat(
    process.env.NEXT_PUBLIC_DEFAULT_LNG || "-76.5320"
  );

  return (
    <div className="flex h-96 w-full items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
      <div className="text-center text-gray-400">
        <p className="text-lg font-medium">🗺️ Mapa Interactivo</p>
        <p className="mt-2 text-sm">
          Centro: {defaultLat.toFixed(4)}, {defaultLng.toFixed(4)}
        </p>
        <p className="mt-1 text-xs">
          Leaflet + OpenStreetMap — Sprint 1
        </p>
      </div>
    </div>
  );
}
