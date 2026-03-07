"use client";

/**
 * Hook — useProducts: obtiene productos del catálogo desde la API.
 *
 * Sprint 0: Estructura base. Sprint 1: Conectar con API real.
 */

import { useState, useEffect } from "react";

interface Product {
  id: string;
  name: string;
  price: number;
  category?: string;
  image_urls: string[];
  is_active: boolean;
}

export function useProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // TODO (Sprint 1): Reemplazar con llamada real a api.get("/products")
    setProducts([]);
    setLoading(false);
  }, []);

  return { products, loading, error };
}
