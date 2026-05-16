"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import MapView from "@/components/MapView";
import SearchBar from "@/components/SearchBar";
import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

interface SearchItem {
  id: string;
  name: string;
  category: string | null;
  seller_lat?: number | null;
  seller_lng?: number | null;
  seller_location_label?: string | null;
  distance_meters?: number | null;
}

interface SearchResponse {
  items: SearchItem[];
}

const DEFAULT_LAT = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || "3.3516");
const DEFAULT_LNG = parseFloat(
  process.env.NEXT_PUBLIC_DEFAULT_LNG || "-76.5320",
);

export default function MapPage() {
  const { token } = useAuth();

  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState("*");
  const [radiusMeters, setRadiusMeters] = useState(500);
  const [zoneEnabled, setZoneEnabled] = useState(true);
  const [centerLat, setCenterLat] = useState(DEFAULT_LAT);
  const [centerLng, setCenterLng] = useState(DEFAULT_LNG);
  const [items, setItems] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMapData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        q: query.trim() || "*",
        limit: "100",
      });

      // Only apply geo filter when zone is enabled
      if (zoneEnabled) {
        params.set("lat", String(centerLat));
        params.set("lng", String(centerLng));
        params.set("radius_meters", String(radiusMeters));
      }

      const response = await api.get<SearchResponse>(
        `/products/search?${params.toString()}`,
        token || undefined,
      );
      setItems(response.items);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No fue posible cargar el mapa",
      );
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [query, radiusMeters, zoneEnabled, centerLat, centerLng, token]);

  useEffect(() => {
    fetchMapData();
  }, [fetchMapData]);

  /** Allow user to tap the map to reposition the search center. */
  const handleSelectCenter = useCallback((lat: number, lng: number) => {
    setCenterLat(lat);
    setCenterLng(lng);
  }, []);

  const handleResetCenter = useCallback(() => {
    setCenterLat(DEFAULT_LAT);
    setCenterLng(DEFAULT_LNG);
  }, []);

  const mapPoints = useMemo(
    () =>
      items
        .filter(
          (item) =>
            typeof item.seller_lat === "number" &&
            typeof item.seller_lng === "number",
        )
        .map((item) => ({
          id: item.id,
          lat: item.seller_lat as number,
          lng: item.seller_lng as number,
          label: item.name,
          subtitle:
            item.seller_location_label || item.category || "Vendedor en campus",
          distanceMeters: item.distance_meters ?? null,
        })),
    [items],
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-gray-900">Mapa del Campus</h1>
      <p className="mt-2 text-sm text-gray-500">
        Vendedores cercanos a UAO, Cali. Haz clic en el mapa para cambiar el
        centro de busqueda.
      </p>

      <div className="mt-6 grid gap-3 lg:grid-cols-[1fr_auto_auto_auto]">
        <SearchBar
          value={queryInput}
          onChange={setQueryInput}
          onSearch={(nextQuery) => setQuery(nextQuery || "*")}
          onClear={() => {
            setQueryInput("");
            setQuery("*");
          }}
          loading={loading}
          placeholder="Filtra lo que quieres ver en el mapa"
        />

        {/* Zone toggle */}
        <label className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={zoneEnabled}
            onChange={(e) => setZoneEnabled(e.target.checked)}
            className="rounded text-vera-600 focus:ring-vera-500"
          />
          Filtrar por zona
        </label>

        {/* Radius selector — only when zone enabled */}
        {zoneEnabled && (
          <label className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600">
            Radio
            <select
              value={radiusMeters}
              onChange={(e) => setRadiusMeters(Number(e.target.value))}
              className="rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-vera-500 focus:outline-none"
            >
              <option value={100}>100 m</option>
              <option value={300}>300 m</option>
              <option value={500}>500 m</option>
              <option value={1000}>1 km</option>
              <option value={2000}>2 km</option>
              <option value={5000}>5 km</option>
            </select>
          </label>
        )}

        {/* Reset center button */}
        {zoneEnabled && (
          <button
            onClick={handleResetCenter}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 transition-colors"
          >
            Centrar en UAO
          </button>
        )}
      </div>

      {!zoneEnabled && (
        <div className="mt-3 p-3 rounded-lg bg-blue-50 border border-blue-200 text-sm text-blue-800">
          Mostrando todos los vendedores sin filtro de zona. Haz clic en
          &quot;Filtrar por zona&quot; para limitar la busqueda a un area
          especifica.
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="mt-6">
        <MapView
          points={mapPoints}
          centerLat={centerLat}
          centerLng={centerLng}
          heightClassName="h-[28rem]"
          radiusMeters={zoneEnabled ? radiusMeters : undefined}
          selectable={zoneEnabled}
          onSelectLocation={handleSelectCenter}
        />
      </div>

      <p className="mt-3 text-xs text-gray-500">
        Resultados: {items.length} productos, {mapPoints.length} con coordenadas
        visibles en mapa.
        {zoneEnabled && (
          <span className="ml-2 text-vera-600">
            Centro: {centerLat.toFixed(4)}, {centerLng.toFixed(4)}
          </span>
        )}
      </p>
    </main>
  );
}
