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
  const [items, setItems] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMapData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        q: query.trim() || "*",
        lat: String(DEFAULT_LAT),
        lng: String(DEFAULT_LNG),
        radius_meters: String(radiusMeters),
        limit: "100",
      });

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
  }, [query, radiusMeters, token]);

  useEffect(() => {
    fetchMapData();
  }, [fetchMapData]);

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
        Vendedores cercanos a UAO, Cali. La búsqueda usa el mismo motor del
        catálogo.
      </p>

      <div className="mt-6 grid gap-3 lg:grid-cols-[1fr_auto]">
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
          </select>
        </label>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="mt-6">
        <MapView
          points={mapPoints}
          centerLat={DEFAULT_LAT}
          centerLng={DEFAULT_LNG}
          heightClassName="h-[28rem]"
          radiusMeters={radiusMeters}
        />
      </div>

      <p className="mt-3 text-xs text-gray-500">
        Resultados: {items.length} productos, {mapPoints.length} con coordenadas
        visibles en mapa.
      </p>
    </main>
  );
}
