"use client";

/**
 * Página — Publicar Nuevo Producto (Sprint 3 — HU 3.1).
 *
 * Solo accesible para vendedores autenticados.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import ProductForm from "@/components/products/ProductForm";

export default function NewProductPage() {
  const router = useRouter();
  const { isAuthenticated, isHydrated, user } = useAuth();

  useEffect(() => {
    if (isHydrated && (!isAuthenticated || user?.role !== "vendedor")) {
      router.push("/products");
    }
  }, [isHydrated, isAuthenticated, user, router]);

  if (!isHydrated || !isAuthenticated || user?.role !== "vendedor") {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Cargando…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">
        Publicar Producto
      </h1>
      <p className="text-sm text-gray-500 mb-8">
        Completa los datos de tu producto para publicarlo en el catálogo.
      </p>

      <ProductForm mode="create" />
    </main>
  );
}
