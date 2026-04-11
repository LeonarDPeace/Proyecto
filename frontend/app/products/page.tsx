"use client";

/**
 * Página — Catálogo de Productos (Sprint 3).
 *
 * Obtiene los productos activos de la API y los muestra en un grid.
 * Incluye filtro por categoría y enlace à "Publicar" para vendedores.
 */

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import ProductCard from "@/components/ProductCard";
import SearchBar from "@/components/SearchBar";

interface Product {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category: string | null;
  image_urls: string[];
  is_active: boolean;
  seller_id: string;
  created_at: string;
  updated_at: string;
  seller_lat?: number | null;
  seller_lng?: number | null;
  seller_location_label?: string | null;
}

interface ProductSearchMeta {
  search_mode: "semantic" | "fallback_fulltext" | "fulltext";
  reason: string | null;
  quota_remaining: number | null;
  quota_limit: number | null;
}

interface ProductSearchResponse {
  items: Product[];
  total: number;
  meta: ProductSearchMeta;
}

interface SearchQuota {
  business_date: string;
  daily_limit: number;
  searches_used: number;
  remaining: number;
}

const CATEGORIES = [
  { value: "", label: "Todas" },
  { value: "comida", label: "🍔 Comida/Supermercado" },
  { value: "tecnologia", label: "💻 Tecnología" },
  { value: "moda", label: "👕 Moda" },
  { value: "hogar", label: "🛋️ Hogar" },
  { value: "deportes", label: "⚽ Deportes" },
  { value: "belleza", label: "💅 Belleza" },
  { value: "academico", label: "📚 Académico" },
  { value: "entretenimiento", label: "🎮 Entretenimiento" },
  { value: "servicios", label: "🔧 Servicios" },
  { value: "vehiculos", label: "🚗 Vehículos" },
  { value: "otros", label: "📦 Otros" },
];

export default function ProductsPage() {
  const { isAuthenticated, user, token } = useAuth();
  const isSeller = user?.role === "vendedor";

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState("");
  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState("");
  const [searchMeta, setSearchMeta] = useState<ProductSearchMeta | null>(null);
  const [quota, setQuota] = useState<SearchQuota | null>(null);

  const fetchQuota = useCallback(async () => {
    if (!token) {
      setQuota(null);
      return;
    }

    try {
      const data = await api.get<SearchQuota>("/users/me/search-quota", token);
      setQuota(data);
    } catch {
      // Si falla, solo ocultamos indicador para no bloquear catálogo.
      setQuota(null);
    }
  }, [token]);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (query.trim()) {
        const params = new URLSearchParams({ q: query.trim(), limit: "50" });
        if (category) {
          params.set("category", category);
        }

        const data = await api.get<ProductSearchResponse>(
          `/products/search?${params.toString()}`,
          token || undefined
        );

        setProducts(data.items);
        setSearchMeta(data.meta);

        if (data.meta.quota_limit !== null && data.meta.quota_remaining !== null) {
          setQuota((prev) => ({
            business_date: prev?.business_date || new Date().toISOString().slice(0, 10),
            daily_limit: data.meta.quota_limit as number,
            searches_used: prev?.daily_limit
              ? Math.max(0, (data.meta.quota_limit as number) - (data.meta.quota_remaining as number))
              : Math.max(0, (data.meta.quota_limit as number) - (data.meta.quota_remaining as number)),
            remaining: data.meta.quota_remaining as number,
          }));
        }
      } else {
        const listQuery = category ? `?category=${category}&limit=50` : "?limit=50";
        const data = await api.get<Product[]>(`/products/${listQuery}`);
        setProducts(data);
        setSearchMeta(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar productos");
    } finally {
      setLoading(false);
    }
  }, [category, query, token]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchQuota();
    } else {
      setQuota(null);
    }
  }, [fetchQuota, isAuthenticated]);

  const searchBanner =
    searchMeta?.search_mode === "semantic"
      ? "Búsqueda inteligente activada"
      : searchMeta?.search_mode === "fallback_fulltext"
      ? "Búsqueda inteligente no disponible, usando full-text"
      : null;

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Catálogo</h1>
          <p className="mt-1 text-sm text-gray-500">
            Productos disponibles en tu campus
          </p>
        </div>

        {isAuthenticated && isSeller && (
          <Link
            href="/products/new"
            className="inline-flex items-center gap-2 rounded-lg bg-vera-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-vera-700 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-5 w-5">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            Publicar Producto
          </Link>
        )}
      </div>

      {/* Búsqueda */}
      <div className="mt-6">
        <SearchBar
          value={queryInput}
          onChange={setQueryInput}
          onSearch={(nextQuery) => setQuery(nextQuery)}
          onClear={() => {
            setQueryInput("");
            setQuery("");
          }}
          loading={loading}
          placeholder="Busca por texto natural: 'algo pa picar', 'mecato', 'audífonos baratos'"
        />
      </div>

      {/* Estado de búsqueda/cuota */}
      {(searchBanner || (isAuthenticated && quota)) && (
        <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          {searchBanner ? (
            <p
              className={`text-xs font-medium ${
                searchMeta?.search_mode === "semantic"
                  ? "text-emerald-700"
                  : "text-amber-700"
              }`}
            >
              {searchBanner}
            </p>
          ) : (
            <span />
          )}

          {isAuthenticated && quota && (
            <p className="text-xs text-gray-600">
              Quedan <span className="font-semibold text-vera-700">{quota.remaining}</span> búsquedas inteligentes hoy
            </p>
          )}
        </div>
      )}

      {/* Filtro de Categoría por Menú Desplegable */}
      <div className="mt-6 flex flex-col sm:flex-row sm:items-center gap-3">
        <label htmlFor="category-select" className="text-sm font-medium text-gray-700">
          Explorar por categoría:
        </label>
        <div className="relative max-w-sm w-full">
          <select
            id="category-select"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setQuery(""); // Resetea el texto para evitar colisiones
              setQueryInput("");
            }}
            className="block w-full appearance-none rounded-lg border border-gray-300 bg-white px-4 py-2.5 pr-10 text-sm font-medium text-gray-700 shadow-sm transition-all focus:border-vera-500 focus:outline-none focus:ring-2 focus:ring-vera-500/20"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-5 w-5">
              <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
          <button onClick={fetchProducts} className="ml-2 underline">
            Reintentar
          </button>
        </div>
      )}

      {/* Grid de productos */}
      {loading ? (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="rounded-lg border border-gray-100 p-4 shadow-sm">
              <div className="aspect-[4/3] w-full bg-gray-200 rounded-md animate-pulse mb-4" />
              <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse mb-3" />
              <div className="h-4 w-1/2 bg-gray-100 rounded animate-pulse mb-4" />
              <div className="h-6 w-1/3 bg-gray-300 rounded animate-pulse" />
            </div>
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="mt-8 rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-3xl mb-3">📦</p>
          <p className="text-gray-500 text-sm">
            {query
              ? "No encontramos resultados para esa búsqueda."
              : category
              ? "No hay productos en esta categoría."
              : "No hay productos publicados aún."}
          </p>
          {isAuthenticated && isSeller && (
            <Link
              href="/products/new"
              className="mt-4 inline-block text-sm font-medium text-vera-600 hover:underline"
            >
              ¡Sé el primero en publicar!
            </Link>
          )}
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <Link key={product.id} href={`/products/${product.id}`}>
              <ProductCard product={product} />
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
