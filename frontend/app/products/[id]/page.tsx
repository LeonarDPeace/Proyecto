"use client";

/**
 * Página — Detalle de Producto (Sprint 3 y 4).
 *
 * Muestra información completa del producto.
 * Si el usuario autenticado es el dueño, muestra acciones de edición.
 * Si es otro usuario, muestra botón para Iniciar Negociación.
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { useNegotiations } from "@/hooks/useNegotiations";
import Button from "@/components/ui/Button";
import ProductCard from "@/components/ProductCard";
import ReportModal from "@/components/ReportModal";

interface Product {
  id: string;
  name: string;
  description: string | null;
  price: number;
  category: string | null;
  image_urls: string[];
  is_active: boolean;
  seller_id: string;
  seller?: SellerPublicInfo | null;
  created_at: string;
  updated_at: string;
  stock?: number;
  discount_percentage?: number;
  warranty_days?: number;
  is_returnable?: boolean;
  fulfillment_type?: string;
  payment_methods?: string[];
  promotions?: string[];
}

interface SellerPublicInfo {
  id: string;
  name: string;
  role: string;
  reputation: number;
  average_rating: number;
  total_reviews: number;
  is_verified: boolean;
  member_since?: string | null;
  last_active_at?: string | null;
  location_label?: string | null;
  location_campus?: string | null;
  email?: string | null;
  phone?: string | null;
}

export default function ProductDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const { user, token, isHydrated } = useAuth();
  const { createNegotiation } = useNegotiations();

  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [acting, setActing] = useState(false);
  const [negotiating, setNegotiating] = useState(false);

  // Sprint 5 Checkout State
  const [showCheckout, setShowCheckout] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [checkoutData, setCheckoutData] = useState({
    quantity: 1,
    payment_method: "",
    buyer_note: "¡Hola! Me interesa este producto.",
  });

  const isOwner =
    isHydrated && user && product && user.id === product.seller_id;

  const fetchProduct = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.get<Product>(`/products/${params.id}`);
      setProduct(data);

      // VeraMatch: Cargar recomendaciones basadas en la categoría
      if (data.category) {
        try {
          const recs = await api.get<Product[]>(
            `/products/?category=${data.category}&limit=5`,
          );
          // Filtramos el producto actual para que no se recomiende a sí mismo
          setRecommendations(recs.filter((p) => p.id !== data.id).slice(0, 3));
        } catch (errRec) {
          // Silently fail recommendations
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Producto no encontrado.");
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
        token,
      );
      setProduct(updated);
    } catch {
      // Silently fail status update
    } finally {
      setActing(false);
    }
  }

  async function handleDelete() {
    if (!product || !token) return;
    if (
      !confirm(
        "¿Estás seguro de eliminar este producto? Esta acción no se puede deshacer.",
      )
    )
      return;

    setActing(true);
    try {
      await api.delete(`/products/${product.id}`, token);
      router.push("/products");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al eliminar.");
      setActing(false);
    }
  }

  async function handleStartNegotiation() {
    if (!product || !token) return;
    setNegotiating(true);
    try {
      const neg = await createNegotiation(
        product.id,
        checkoutData.buyer_note,
        {
          quantity: checkoutData.quantity,
          payment_method: checkoutData.payment_method || (product.payment_methods?.[0] || "efectivo"),
        }
      );
      router.push(`/negotiations/${neg.id}`);
    } catch (err: any) {
      alert(
        err.message ||
          "Error al iniciar negociación. Es posible que ya tengas una en curso.",
      );
      setNegotiating(false);
    }
  }

  const formattedPrice = product
    ? new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        minimumFractionDigits: 0,
      }).format(product.price)
    : "";

  const sellerRating = product?.seller?.average_rating ?? 0;
  const sellerReviews = product?.seller?.total_reviews ?? 0;

  const sellerMemberSince = product?.seller?.member_since
    ? new Date(product.seller.member_since).toLocaleDateString("es-CO")
    : "Sin datos";
  const sellerLastActive = product?.seller?.last_active_at
    ? new Date(product.seller.last_active_at).toLocaleString("es-CO")
    : "Sin datos";

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
        <Link
          href="/products"
          className="hover:text-vera-600 transition-colors"
        >
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
        <div className="flex items-center justify-between w-full">
          <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
          <button 
            onClick={() => setIsReportOpen(true)}
            className="text-gray-400 hover:text-red-500 transition-colors ml-4"
            title="Denunciar publicación"
          >
            🚩
          </button>
        </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {product.category && (
              <span className="inline-block rounded-full bg-vera-50 px-3 py-0.5 text-xs font-medium text-vera-700">
                {product.category}
              </span>
            )}
            {product.stock !== undefined && (
              <span className={`inline-block rounded-full px-3 py-0.5 text-xs font-medium ${product.stock > 0 ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                {product.stock > 0 ? `${product.stock} disponibles` : "Agotado"}
              </span>
            )}
          </div>
        </div>
        <div className="text-right">
          {product.discount_percentage && product.discount_percentage > 0 ? (
            <>
              <p className="text-sm text-gray-400 line-through">
                {new Intl.NumberFormat("es-CO", {
                  style: "currency",
                  currency: "COP",
                  minimumFractionDigits: 0,
                }).format(product.price / (1 - product.discount_percentage / 100))}
              </p>
              <p className="text-3xl font-bold text-vera-600">
                {formattedPrice}
                <span className="text-sm text-red-500 ml-2">-{product.discount_percentage}%</span>
              </p>
            </>
          ) : (
            <p className="text-3xl font-bold text-vera-600">{formattedPrice}</p>
          )}
          <p
            className={`mt-1 text-xs font-medium ${
              product.is_active ? "text-green-600" : "text-red-500"
            }`}
          >
            {product.is_active ? "✅ Disponible" : "⛔ No disponible"}
          </p>
        </div>
      </div>

      {/* Características Avanzadas */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div>
          <p className="text-xs text-gray-500">Garantía</p>
          <p className="text-sm font-semibold">{product.warranty_days ? `${product.warranty_days} días` : "Sin garantía"}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Devolución</p>
          <p className="text-sm font-semibold">{product.is_returnable ? "Aceptada" : "No aceptada"}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Fulfillment</p>
          <p className="text-sm font-semibold capitalize">{product.fulfillment_type || "merchant"}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Pagos aceptados</p>
          <p className="text-sm font-semibold capitalize whitespace-pre-wrap">
            {product.payment_methods?.join(", ") || "efectivo"}
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

      {product.seller && (
        <section className="mt-6 rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-700">
                Vendedor
              </h2>
              <Link href={`/users/${product.seller.id}`} className="text-sm font-semibold text-vera-600 hover:underline">
                {product.seller.name}
              </Link>
              <p className="text-xs text-gray-500">
                Miembro desde: {sellerMemberSince}
              </p>
              {(product.seller.location_label ||
                product.seller.location_campus) && (
                <p className="text-xs text-gray-500">
                  Ubicación: {product.seller.location_label || ""}
                  {product.seller.location_label &&
                  product.seller.location_campus
                    ? " · "
                    : ""}
                  {product.seller.location_campus || ""}
                </p>
              )}
            </div>
            <div className="text-sm text-gray-600 sm:text-right">
              <p className="font-semibold">
                ⭐ {sellerRating.toFixed(1)}
                <span className="text-xs text-gray-500">
                  {` (${sellerReviews})`}
                </span>
              </p>
              <p className="text-xs text-gray-500">
                {product.seller.is_verified
                  ? "Vendedor verificado"
                  : "Vendedor sin verificación"}
              </p>
            </div>
          </div>

          <div className="mt-3 grid grid-cols-1 gap-2 text-xs text-gray-600 sm:grid-cols-2">
            {product.seller.email ? <p>Email: {product.seller.email}</p> : <p>Email: <span className="italic text-gray-400">Protegido por privacidad</span></p>}
            {product.seller.phone ? <p>Teléfono: {product.seller.phone}</p> : <p>Teléfono: <span className="italic text-gray-400">Protegido por privacidad</span></p>}
            <p>Última actividad: {sellerLastActive}</p>
          </div>
        </section>
      )}

      {/* Acciones principales (Dueño vs Comprador) */}
      <div className="mt-8">
        {isOwner ? (
          <section className="rounded-xl border border-vera-200 bg-vera-50/50 p-5">
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
        ) : product.is_active ? (
          <div className="flex flex-col gap-4 sm:flex-row">
            {isHydrated && user ? (
              <>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => setShowCheckout(true)}
                  disabled={negotiating}
                  className="w-full sm:w-auto text-lg px-8 py-3 shadow-md"
                >
                  💬 Contactar al vendedor / Comprar
                </Button>

                {/* Checkout Modal */}
                {showCheckout && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
                      <h3 className="text-xl font-bold text-gray-900 mb-4">Detalles de la compra</h3>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Cantidad</label>
                          <input 
                            type="number" 
                            min="1" 
                            max={product.stock || 1} 
                            value={checkoutData.quantity}
                            onChange={e => setCheckoutData({...checkoutData, quantity: parseInt(e.target.value) || 1})}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Método de pago preferido</label>
                          <select
                            value={checkoutData.payment_method || (product.payment_methods?.[0] || "")}
                            onChange={e => setCheckoutData({...checkoutData, payment_method: e.target.value})}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500 capitalize"
                          >
                            {product.payment_methods && product.payment_methods.length > 0 ? (
                              product.payment_methods.map(pm => (
                                <option key={pm} value={pm}>{pm}</option>
                              ))
                            ) : (
                              <option value="efectivo">Efectivo</option>
                            )}
                          </select>
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Mensaje para el vendedor</label>
                          <textarea 
                            rows={2}
                            value={checkoutData.buyer_note}
                            onChange={e => setCheckoutData({...checkoutData, buyer_note: e.target.value})}
                            className="block w-full rounded-lg border border-gray-300 px-3 py-2 shadow-sm focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
                          />
                        </div>
                      </div>

                      <div className="mt-6 flex justify-end gap-3">
                        <Button variant="outline" size="md" onClick={() => setShowCheckout(false)} disabled={negotiating}>Cancelar</Button>
                        <Button variant="primary" size="md" onClick={handleStartNegotiation} disabled={negotiating}>
                          {negotiating ? "Procesando..." : "Confirmar Compra"}
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : isHydrated && !user ? (
              <Link href="/auth" className="w-full sm:w-auto">
                <Button variant="primary" size="lg" className="w-full">
                  Inicia sesión para comprar
                </Button>
              </Link>
            ) : null}
          </div>
        ) : null}
      </div>

      {/* Metadata */}
      <div className="mt-6 border-t border-gray-100 pt-4 flex gap-4 text-xs text-gray-400">
        <span>
          Publicado: {new Date(product.created_at).toLocaleDateString("es-CO")}
        </span>
        <span>
          Actualizado:{" "}
          {new Date(product.updated_at).toLocaleDateString("es-CO")}
        </span>
      </div>

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
      {/* Report Modal */}
      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        productId={product.id}
        targetName={product.name}
      />
    </main>
  );
}
