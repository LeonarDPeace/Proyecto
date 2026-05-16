"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

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
  discount_percentage?: number;
  stock?: number;
  is_returnable?: boolean;
}

interface ProductSearchMeta {
  search_mode: "semantic" | "fallback_fulltext" | "fulltext";
  reason: string | null;
  quota_remaining: number | null;
  quota_limit: number | null;
  category_applied?: string | null;
  subcategory_applied?: string | null;
  condition_applied?: string | null;
  brand_applied?: string | null;
  has_free_shipping_applied?: boolean | null;
  min_price_applied?: number | null;
  max_price_applied?: number | null;
  tags_applied?: string[];
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

interface Filters {
  category: string;
  min_price: string;
  max_price: string;
  availability: string;
  warranty: string;
  payment_methods: string[];
}

const CATEGORIES = [
  { value: "", label: "Todas" },
  { value: "comida", label: "🍔 Comida" },
  { value: "tecnologia", label: "💻 Tecnología" },
  { value: "moda", label: "👕 Moda" },
  { value: "academico", label: "📚 Académico" },
  { value: "servicios", label: "🔧 Servicios" },
  { value: "otros", label: "📦 Otros" },
];

export default function ProductsPage() {
  const { isAuthenticated, user, token } = useAuth();
  const isSeller = user?.role === "vendedor";

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState("");
  const [searchMode, setSearchMode] = useState<"standard" | "smart" | null>(null);
  
  const [filters, setFilters] = useState<Filters>({
    category: "",
    min_price: "",
    max_price: "",
    availability: "",
    warranty: "",
    payment_methods: [],
  });

  const [searchMeta, setSearchMeta] = useState<ProductSearchMeta | null>(null);
  const [quota, setQuota] = useState<SearchQuota | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isMounted, setIsMounted] = useState(false);

  // HU 8.8: Persistencia del modo de visualización
  useEffect(() => {
    setIsMounted(true);
    const saved = localStorage.getItem("veramarket_catalog_view");

    if (saved === "grid" || saved === "list") setViewMode(saved);
  }, []);

  useEffect(() => {
    localStorage.setItem("veramarket_catalog_view", viewMode);
  }, [viewMode]);

  // Sincronización reactiva: si el input está vacío, limpiar la búsqueda automáticamente
  useEffect(() => {
    if (queryInput === "" && query !== "") {
      setQuery("");
      setSearchMode(null);
    }
  }, [queryInput, query]);

  const fetchQuota = useCallback(async () => {

    if (!token) return;
    try {
      const data = await api.get<SearchQuota>("/users/me/search-quota", token);
      setQuota(data);
    } catch {
      setQuota(null);
    }
  }, [token]);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      let activeFilters: any = {};
      if (filters.category) activeFilters.category = filters.category;
      if (filters.min_price) activeFilters.min_price = parseFloat(filters.min_price);
      if (filters.max_price) activeFilters.max_price = parseFloat(filters.max_price);
      if (filters.availability) activeFilters.availability = filters.availability;
      if (filters.warranty) activeFilters.warranty = filters.warranty;
      if (filters.payment_methods.length > 0) activeFilters.payment_methods = filters.payment_methods;

      if (query.trim() || Object.keys(activeFilters).length > 0) {
        let data: ProductSearchResponse;

        if (searchMode === "smart") {
          data = await api.post<ProductSearchResponse>(
            "/products/search/intelligent",
            {
              query: query.trim() || "all",
              filters: activeFilters,
              limit: 50,
            },
            token || undefined,
          );
        } else {
          const params = new URLSearchParams({
            q: query.trim() || "*",
            limit: "50",
            use_semantic: "false",
          });
          Object.entries(activeFilters).forEach(([k, v]) => {
            if (Array.isArray(v)) v.forEach(val => params.append(k, val));
            else params.set(k, String(v));
          });

          data = await api.get<ProductSearchResponse>(
            `/products/search?${params.toString()}`,
            token || undefined,
          );
        }

        setProducts(data.items);
        setSearchMeta(data.meta);

        // Sync quota from search response — always use server business_date
        if (data.meta.quota_limit !== null && data.meta.quota_remaining !== null) {
          setQuota({
            business_date: new Date().toISOString().slice(0, 10),
            daily_limit: data.meta.quota_limit as number,
            searches_used: (data.meta.quota_limit as number) - (data.meta.quota_remaining as number),
            remaining: data.meta.quota_remaining as number,
          });
        }
      } else {
        const data = await api.get<Product[]>("/products/?limit=50");
        setProducts(data);
        setSearchMeta(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar productos");
    } finally {
      setLoading(false);
    }
  }, [filters, query, searchMode, token]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  // Force-refresh quota on mount and whenever auth state changes
  // This ensures the daily reset is reflected even if the user
  // navigated to the page without triggering a search.
  useEffect(() => {
    if (isAuthenticated) {
      fetchQuota();
    } else {
      setQuota(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, token]);

  const togglePaymentMethod = (method: string) => {
    setFilters(prev => ({
      ...prev,
      payment_methods: prev.payment_methods.includes(method)
        ? prev.payment_methods.filter(m => m !== method)
        : [...prev.payment_methods, method]
    }));
  };

  const applySearch = (nextQuery: string, mode: "standard" | "smart") => {
    setSearchMode(mode);
    setQuery(nextQuery);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 sm:px-6 lg:px-8 flex flex-col md:flex-row gap-6">
        
        {/* Mobile Sidebar Toggle */}
        <div className="md:hidden flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Catálogo</h1>
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 bg-white rounded-md shadow-sm border border-gray-200"
          >
            Filtros
          </button>
        </div>

        {/* Sidebar Filters */}
        <AnimatePresence>
          {isMounted && (isSidebarOpen || window.innerWidth >= 768) && (
            <motion.aside 
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              className={`fixed md:relative z-40 inset-y-0 left-0 w-64 bg-white/80 backdrop-blur-xl border-r md:border border-gray-200 p-6 md:rounded-2xl shadow-xl md:shadow-sm overflow-y-auto ${!isSidebarOpen && 'hidden md:block'}`}
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-bold text-gray-900">Filtros</h2>
                <button className="md:hidden" onClick={() => setIsSidebarOpen(false)}>✕</button>
              </div>

              {/* Categorías */}
              <div className="mb-6">
                <h3 className="font-semibold text-sm text-gray-700 mb-3">Categoría</h3>
                <div className="space-y-2">
                  {CATEGORIES.map(cat => (
                    <label key={cat.value} className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        name="category"
                        checked={filters.category === cat.value}
                        onChange={() => setFilters({ ...filters, category: cat.value })}
                        className="text-vera-600 focus:ring-vera-500"
                      />
                      <span className="text-sm text-gray-700">{cat.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Precio */}
              <div className="mb-6">
                <h3 className="font-semibold text-sm text-gray-700 mb-3">Precio (COP)</h3>
                <div className="flex gap-2">
                  <input 
                    type="number" 
                    placeholder="Min" 
                    value={filters.min_price}
                    onChange={(e) => setFilters({ ...filters, min_price: e.target.value })}
                    className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:ring-1 focus:ring-vera-500"
                  />
                  <input 
                    type="number" 
                    placeholder="Max" 
                    value={filters.max_price}
                    onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
                    className="w-full px-3 py-1.5 text-sm border border-gray-200 rounded-md focus:ring-1 focus:ring-vera-500"
                  />
                </div>
              </div>

              {/* Disponibilidad */}
              <div className="mb-6">
                <h3 className="font-semibold text-sm text-gray-700 mb-3">Disponibilidad</h3>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    checked={filters.availability === "in_stock"}
                    onChange={(e) => setFilters({ ...filters, availability: e.target.checked ? "in_stock" : "" })}
                    className="rounded text-vera-600 focus:ring-vera-500"
                  />
                  <span className="text-sm text-gray-700">En stock</span>
                </label>
              </div>

              {/* Métodos de Pago */}
              <div className="mb-6">
                <h3 className="font-semibold text-sm text-gray-700 mb-3">Medios de Pago</h3>
                <div className="space-y-2">
                  {["efectivo", "transferencia", "tarjeta"].map(method => (
                    <label key={method} className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="checkbox"
                        checked={filters.payment_methods.includes(method)}
                        onChange={() => togglePaymentMethod(method)}
                        className="rounded text-vera-600 focus:ring-vera-500"
                      />
                      <span className="text-sm text-gray-700 capitalize">{method}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button 
                onClick={() => {
                  setFilters({ category: "", min_price: "", max_price: "", availability: "", warranty: "", payment_methods: [] });
                  setQuery("");
                  setQueryInput("");
                  setSearchMode(null);
                }}
                className="w-full mt-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Limpiar Filtros
              </button>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Content Area */}
        <div className="flex-1 w-full">
          <div className="hidden md:flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Catálogo P2P</h1>
              <p className="mt-1 text-sm text-gray-500">Encuentra productos cerca de ti.</p>
            </div>
            <div className="flex items-center gap-4">
              {/* HU 8.8: Layout Toggle */}
              <div className="flex bg-gray-100 p-1 rounded-xl border border-gray-200">
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-2 rounded-lg transition-all ${viewMode === "grid" ? "bg-white shadow-sm text-vera-600" : "text-gray-400 hover:text-gray-600"}`}
                  title="Vista Cuadrícula"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="7" rx="1" />
                    <rect x="14" y="3" width="7" height="7" rx="1" />
                    <rect x="14" y="14" width="7" height="7" rx="1" />
                    <rect x="3" y="14" width="7" height="7" rx="1" />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-2 rounded-lg transition-all ${viewMode === "list" ? "bg-white shadow-sm text-vera-600" : "text-gray-400 hover:text-gray-600"}`}
                  title="Vista Lista"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="8" y1="6" x2="21" y2="6" />
                    <line x1="8" y1="12" x2="21" y2="12" />
                    <line x1="8" y1="18" x2="21" y2="18" />
                    <line x1="3" y1="6" x2="3.01" y2="6" />
                    <line x1="3" y1="12" x2="3.01" y2="12" />
                    <line x1="3" y1="18" x2="3.01" y2="18" />
                  </svg>
                </button>
              </div>

              {isAuthenticated && isSeller && (
                <Link href="/products/new">
                  <motion.button 
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="bg-vera-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold shadow-md shadow-vera-600/30"
                  >
                    + Publicar Producto
                  </motion.button>
                </Link>
              )}
            </div>
          </div>

          <SearchBar
            value={queryInput}
            onChange={setQueryInput}
            onSearch={(nextQuery) => applySearch(nextQuery, "standard")}
            onSmartSearch={(nextQuery) => applySearch(nextQuery, "smart")}
            smartLoading={loading && searchMode === "smart"}
            onClear={() => { setQueryInput(""); setQuery(""); setSearchMode(null); }}
            loading={loading}
            placeholder="Ej: audífonos baratos, mecato con transferencia..."
          />

          {/* Quota & Meta */}
          <div className="mt-4 flex flex-wrap justify-between items-center gap-2">
            {searchMeta?.search_mode === "semantic" && (
               <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                 ✨ Búsqueda Inteligente (Gemini AI)
               </span>
            )}
            {isAuthenticated && quota && (
              <span className="text-xs text-gray-500">
                Cuota IA: <strong className="text-vera-600">{quota.remaining}</strong> restantes hoy
              </span>
            )}
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-50 text-red-700 text-sm rounded-xl border border-red-100">
              {error}
            </div>
          )}

          {/* Grid/List Container */}
          {loading ? (
            <div className={`mt-8 ${viewMode === "grid" ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" : "space-y-4"}`}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className={`bg-gray-100 rounded-2xl animate-pulse ${viewMode === "grid" ? "h-64" : "h-32"}`} />
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="mt-12 text-center">
              <span className="text-4xl">📭</span>
              <p className="mt-4 text-gray-500 font-medium">No se encontraron resultados.</p>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              className={`mt-8 ${viewMode === "grid" ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" : "flex flex-col gap-4"}`}
            >
              {products.map((product, i) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Link href={`/products/${product.id}`}>
                    <ProductCard product={product} variant={viewMode} />
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          )}

        </div>
      </main>
    </div>
  );
}
