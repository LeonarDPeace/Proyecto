"use client";

/**
 * Página — Detalle de Producto (Sprint 3).
 *
 * Muestra información completa del producto.
 * Si el usuario autenticado es el dueño, muestra acciones de edición/eliminación/toggle.
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
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

export default function ProductDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const { user, token, isHydrated } = useAuth();

  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [acting, setActing] = useState(false);

  const isOwner = isHydrated && user && product && user.id === product.seller_id;

  const fetchProduct = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<Product>(`/products/${params.id}`);
      setProduct(data);
      
      // VeraMatch: Cargar recomendaciones basadas en la categoría
      if (data.category) {
        try {
          const recs = await api.get<Product[]>(`/products/?category=${data.category}&limit=5`);
          // Filtramos el producto actual para que no se recomiende a sí mismo
          setRecommendations(recs.filter(p => p.id !== data.id).slice(0, 3));
        } catch (errRec) {
          console.error("No se pudieron cargar recomendaciones", errRec);
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Producto no encontrado."
      );
    } finally {
      setLoading(false);
    }
  }, [params.id]);

  useEffect(() => {
    fetchProduct();
  }, [fetchProduct]);

  async function handleToggleStatus() {
    if (!product || !token) return;
    setActing(true);
    try {
      const updated = await api.patch<Product>(
        `/products/${product.id}/status`,
        undefined,
        token
      );
      setProduct(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al cambiar estado.");
    } finally {
      setActing(false);
    }
  }

  async function handleDelete() {
    if (!product || !token) return;
    if (!confirm("¿Estás seguro de eliminar este producto? Esta acción no se puede deshacer.")) return;

    setActing(true);
    try {
      await api.delete(`/products/${product.id}`, token);
      router.push("/products");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al eliminar.");
      setActing(false);
    }
  }

  const formattedPrice = product
    ? new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        minimumFractionDigits: 0,
      }).format(product.price)
    : "";

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 w-1/2 bg-gray-200 rounded mb-4" />
          <div className="aspect-video w-full bg-gray-200 rounded-lg mb-6" />
          <div className="h-6 w-1/3 bg-gray-200 rounded mb-3" />
          <div className="h-4 w-full bg-gray-100 rounded mb-2" />
          <div className="h-4 w-2/3 bg-gray-100 rounded" />
        </div>
      </main>
    );
  }

  if (error || !product) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8 text-center">
        <p className="text-3xl mb-4">😔</p>
        <p className="text-gray-500">{error || "Producto no encontrado."}</p>
        <Link
          href="/products"
          className="mt-4 inline-block text-sm font-medium text-vera-600 hover:underline"
        >
          ← Volver al catálogo
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      {/* Breadcrumb */}
      <nav className="mb-6 text-sm text-gray-400">
        <Link href="/products" className="hover:text-vera-600 transition-colors">
          Catálogo
        </Link>
        <span className="mx-2">›</span>
        <span className="text-gray-600">{product.name}</span>
      </nav>

      {/* Imagen */}
      <div className="mb-6 overflow-hidden rounded-xl bg-gray-100">
        {product.image_urls.length > 0 ? (
          <div className="flex gap-2 overflow-x-auto p-2">
            {product.image_urls.map((url, i) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                key={i}
                src={url}
                alt={`${product.name} - foto ${i + 1}`}
                className="h-64 w-auto rounded-lg object-cover flex-shrink-0"
              />
            ))}
          </div>
        ) : (
          <div className="flex h-64 items-center justify-center text-gray-400">
            <span className="text-6xl">📦</span>
          </div>
        )}
      </div>

      {/* Info principal */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
          {product.category && (
            <span className="mt-2 inline-block rounded-full bg-vera-50 px-3 py-0.5 text-xs font-medium text-vera-700">
              {product.category}
            </span>
          )}
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-vera-600">{formattedPrice}</p>
          <p
            className={`mt-1 text-xs font-medium ${
              product.is_active ? "text-green-600" : "text-red-500"
            }`}
          >
            {product.is_active ? "✅ Disponible" : "⛔ No disponible"}
          </p>
        </div>
      </div>

      {/* Descripción */}
      {product.description && (
        <div className="mt-6 rounded-xl bg-gray-50 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-2">
            Descripción
          </h2>
          <p className="text-sm text-gray-600 whitespace-pre-wrap">
            {product.description}
          </p>
        </div>
      )}

      {/* Metadata */}
      <div className="mt-4 flex gap-4 text-xs text-gray-400">
        <span>
          Publicado: {new Date(product.created_at).toLocaleDateString("es-CO")}
        </span>
        <span>
          Actualizado: {new Date(product.updated_at).toLocaleDateString("es-CO")}
        </span>
      </div>

      {/* Acciones del dueño */}
      {isOwner && (
        <section className="mt-8 rounded-xl border border-vera-200 bg-vera-50/50 p-5">
          <h3 className="text-sm font-semibold text-vera-700 mb-4">
            Gestión del producto
          </h3>
          <div className="flex flex-wrap gap-3">
            <Link href={`/products/${product.id}/edit`}>
              <Button variant="primary" size="md">
                ✏️ Editar
              </Button>
            </Link>
            <Button
              variant="outline"
              size="md"
              onClick={handleToggleStatus}
              disabled={acting}
            >
              {acting
                ? "Cambiando…"
                : product.is_active
                ? "⏸️ Pausar"
                : "▶️ Activar"}
            </Button>
            <Button
              variant="secondary"
              size="md"
              onClick={handleDelete}
              disabled={acting}
              className="!text-red-600 !bg-red-50 hover:!bg-red-100"
            >
              🗑️ Eliminar
            </Button>
          </div>
        </section>
      )}

      {/* VeraMatch - Recomendaciones (HU 4.3) */}
      {recommendations.length > 0 && (
        <section className="mt-12">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            ✨ VeraMatch 
            <span className="text-sm font-normal text-gray-500">
              Productos similares en tu campus
            </span>
          </h3>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((rec) => (
              <Link key={rec.id} href={`/products/${rec.id}`}>
                <ProductCard product={rec} />
              </Link>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
