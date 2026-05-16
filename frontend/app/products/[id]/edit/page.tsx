"use client";

/**
 * Página — Editar Producto (Sprint 3 — HU 3.2).
 *
 * Carga el producto existente y pre-llena el formulario.
 * Solo accesible para el dueño del producto.
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import ProductForm from "@/components/products/ProductForm";

interface Product {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category: string | null;
  image_urls: string[];
  is_active: boolean;
  seller_id: string;
  stock?: number;
  discount_percentage?: number;
  warranty_days?: number;
  is_returnable?: boolean;
  fulfillment_type?: string;
  payment_methods?: string[];
}

export default function EditProductPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const { user, isAuthenticated, isHydrated } = useAuth();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.get<Product>(`/products/${params.id}`);
        setProduct(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "No se pudo cargar el producto.",
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.id]);

  // Redirect if not owner
  useEffect(() => {
    if (isHydrated && product && user) {
      if (!isAuthenticated || user.id !== product.seller_id) {
        router.push(`/products/${params.id}`);
      }
    }
  }, [isHydrated, isAuthenticated, user, product, router, params.id]);

  if (loading) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 w-1/3 bg-gray-200 rounded mb-6" />
          <div className="space-y-4">
            <div className="h-10 w-full bg-gray-100 rounded" />
            <div className="h-20 w-full bg-gray-100 rounded" />
            <div className="h-10 w-1/2 bg-gray-100 rounded" />
          </div>
        </div>
      </main>
    );
  }

  if (error || !product) {
    return (
      <main className="mx-auto max-w-2xl px-4 py-8 text-center">
        <p className="text-gray-500">{error || "Producto no encontrado."}</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Editar Producto</h1>
      <p className="text-sm text-gray-500 mb-8">
        Modifica los campos que necesites y guarda tus cambios.
      </p>

      <ProductForm
        mode="edit"
        productId={product.id}
        initialData={{
          name: product.name,
          description: product.description || "",
          price: String(product.price),
          category: product.category || "otros",
          stock: String(product.stock ?? 1),
          discount_percentage: String(product.discount_percentage ?? 0),
          warranty_days: String(product.warranty_days ?? 0),
          is_returnable: product.is_returnable ?? false,
          fulfillment_type: product.fulfillment_type ?? "merchant",
          image_urls: product.image_urls.join(", "),
          payment_methods: product.payment_methods ?? ["efectivo"],
        }}
      />
    </main>
  );
}
