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
}

const CATEGORIES = [
  { value: "", label: "Todas" },
  { value: "comida", label: "🍕 Comida" },
  { value: "tecnologia", label: "💻 Tecnología" },
  { value: "ropa", label: "👕 Ropa" },
  { value: "servicios", label: "🔧 Servicios" },
  { value: "libros", label: "📚 Libros" },
  { value: "otros", label: "📦 Otros" },
];

export default function ProductsPage() {
  const { isAuthenticated, user } = useAuth();
  const isSeller = user?.role === "vendedor";

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState("");

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const query = category ? `?category=${category}&limit=50` : "?limit=50";
      const data = await api.get<Product[]>(`/products/${query}`);
      setProducts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar productos");
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

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

      {/* Filtros de categoría */}
      <div className="mt-6 flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setCategory(cat.value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-all ${
              category === cat.value
                ? "bg-vera-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {cat.label}
          </button>
        ))}
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
            {category
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
