"use client";

/**
 * ProductManager — Panel de gestión de productos del vendedor (Sprint 3).
 *
 * Se muestra en la página de perfil. Lista los productos del vendedor
 * y permite cambiar estado (activo/pausado) o eliminar.
 */

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";

interface Product {
  id: string;
  name: string;
  price: number;
  category: string | null;
  image_urls: string[];
  is_active: boolean;
  seller_id: string;
  created_at: string;
}

export default function ProductManager() {
  const { user, token } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);

  const fetchMyProducts = useCallback(async () => {
    if (!user || !token) return;
    setLoading(true);
    try {
      const data = await api.get<Product[]>("/products/mine", token);
      setProducts(data);
    } catch {
      // Silently fail — the section won't show errors as it's supplementary
    } finally {
      setLoading(false);
    }
  }, [user, token]);

  useEffect(() => {
    fetchMyProducts();
  }, [fetchMyProducts]);

  async function handleToggle(productId: string) {
    if (!token) return;
    setActing(productId);
    try {
      const updated = await api.patch<Product>(
        `/products/${productId}/status`,
        undefined,
        token
      );
      setProducts((prev) =>
        prev.map((p) => (p.id === productId ? { ...p, is_active: updated.is_active } : p))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al cambiar estado.");
    } finally {
      setActing(null);
    }
  }

  async function handleDelete(productId: string) {
    if (!token) return;
    if (!confirm("¿Eliminar este producto del catálogo?")) return;

    setActing(productId);
    try {
      await api.delete(`/products/${productId}`, token);
      setProducts((prev) => prev.filter((p) => p.id !== productId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al eliminar.");
    } finally {
      setActing(null);
    }
  }

  const formattedPrice = (price: number) =>
    new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      minimumFractionDigits: 0,
    }).format(price);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="flex items-center gap-4 rounded-lg border border-gray-100 p-4 animate-pulse">
            <div className="h-12 w-12 rounded bg-gray-200" />
            <div className="flex-1">
              <div className="h-4 w-1/2 bg-gray-200 rounded mb-2" />
              <div className="h-3 w-1/4 bg-gray-100 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
        <p className="text-2xl mb-2">📦</p>
        <p className="text-sm text-gray-500 mb-3">
          Aún no has publicado ningún producto.
        </p>
        <Link
          href="/products/new"
          className="inline-block text-sm font-medium text-vera-600 hover:underline"
        >
          ¡Publica tu primer producto!
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {products.map((product) => (
        <div
          key={product.id}
          className="flex flex-col sm:flex-row items-start sm:items-center gap-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
        >
          {/* Thumbnail */}
          <div className="h-14 w-14 flex-shrink-0 rounded-lg bg-gray-100 flex items-center justify-center overflow-hidden">
            {product.image_urls.length > 0 ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={product.image_urls[0]}
                alt={product.name}
                className="h-full w-full object-cover"
              />
            ) : (
              <span className="text-2xl">📦</span>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <Link
              href={`/products/${product.id}`}
              className="font-semibold text-gray-900 hover:text-vera-600 transition-colors truncate block"
            >
              {product.name}
            </Link>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm font-bold text-vera-600">
                {formattedPrice(product.price)}
              </span>
              <span
                className={`inline-flex items-center gap-1 text-xs font-medium ${
                  product.is_active ? "text-green-600" : "text-red-500"
                }`}
              >
                <span className={`h-1.5 w-1.5 rounded-full ${product.is_active ? "bg-green-500" : "bg-red-400"}`} />
                {product.is_active ? "Activo" : "Pausado"}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 flex-shrink-0">
            <Link href={`/products/${product.id}/edit`}>
              <Button variant="outline" size="sm">
                ✏️
              </Button>
            </Link>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleToggle(product.id)}
              disabled={acting === product.id}
            >
              {product.is_active ? "⏸️" : "▶️"}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handleDelete(product.id)}
              disabled={acting === product.id}
              className="!text-red-600 hover:!bg-red-50"
            >
              🗑️
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
