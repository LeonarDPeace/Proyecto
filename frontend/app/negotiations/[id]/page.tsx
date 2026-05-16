"use client";

/**
 * Negotiation Detail Page — Chat + Actions (Sprint 4).
 *
 * Integra:
 * - HU 6.1: Chat en tiempo real (ChatBox)
 * - HU 6.2/6.3: Deep Links de pago (PaymentButtons)
 * - HU 6.4: Confirmación de entrega (DeliveryConfirmation)
 */

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useNegotiations, Negotiation } from "@/hooks/useNegotiations";
import ChatBox from "@/components/chat/ChatBox";
import PaymentButtons from "@/components/chat/PaymentButtons";
import DeliveryConfirmation from "@/components/chat/DeliveryConfirmation";
import OrderTimeline from "@/components/OrderTimeline";
import NegotiationInvoice from "@/components/chat/NegotiationInvoice";
import api from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  pending: "⏳ Pendiente",
  accepted: "✅ Aceptada",
  paused: "⏸️ Pausada",
  rejected: "❌ Rechazada",
  cancelled: "⛔ Cancelada",
  delivered: "🎉 Entregada",
};

export default function NegotiationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const negotiationId = params?.id as string;
  const { user, token, isAuthenticated, isHydrated } = useAuth();
  const { updateStatus } = useNegotiations();

  const [negotiation, setNegotiation] = useState<Negotiation | null>(null);
  const [productName, setProductName] = useState<string>("Producto");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isHydrated, isAuthenticated, router]);

  // Cargar detalle de la negociación
  useEffect(() => {
    if (!token || !negotiationId) return;

    const fetchDetail = async () => {
      setLoading(true);
      try {
        const data = await api.get<Negotiation>(
          `/negotiations/${negotiationId}`,
          token,
        );
        setNegotiation(data);

        // Cargar nombre del producto
        if (data.product_id) {
          try {
            const product = await api.get<any>(`/products/${data.product_id}`);
            setProductName(product.name);
          } catch {
            // Fallback al nombre genérico
          }
        }
      } catch (err: any) {
        setError(err.message || "Error al cargar la negociación");
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [token, negotiationId]);

  const handleAcceptReject = async (
    status: "accepted" | "paused" | "rejected" | "cancelled",
  ) => {
    setActionLoading(true);
    try {
      const updated = await updateStatus(negotiationId, status);
      setNegotiation(updated);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeliveryConfirmed = async () => {
    // Re-fetch negotiation to get updated state
    if (!token) return;
    try {
      const data = await api.get<Negotiation>(
        `/negotiations/${negotiationId}`,
        token,
      );
      setNegotiation(data);
    } catch {
      // Silently fail — UI already shows optimistic update
    }
  };

  const formatPrice = (price: number | null) => {
    if (!price) return "—";
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (!isHydrated || loading) {
    return (
      <main className="neg-detail-page">
        <div className="neg-loading">
          <div className="neg-loading-spinner" />
          <span>Cargando negociación…</span>
        </div>
      </main>
    );
  }

  if (error || !negotiation) {
    return (
      <main className="neg-detail-page">
        <div className="neg-error-full">
          <p>{error || "Negociación no encontrada"}</p>
          <button
            className="neg-back-btn"
            onClick={() => router.push("/negotiations")}
          >
            ← Volver a Negociaciones
          </button>
        </div>
      </main>
    );
  }

  const isBuyer = user?.id === negotiation.buyer_id;
  const isSeller = user?.id === negotiation.seller_id;
  const canChat =
    negotiation.status === "pending" || negotiation.status === "accepted";

  return (
    <main className="neg-detail-page">
      <div className="neg-detail-container">
        {/* Back button */}
        <button
          className="neg-back-btn"
          onClick={() => router.push("/negotiations")}
        >
          ← Mis Negociaciones
        </button>

        {/* Order Timeline (HU 8.1) */}
        <OrderTimeline status={negotiation.status} />

        {/* Action Buttons (HU 8.1) */}
        <div className="neg-actions mb-6">
          {/* Acciones del Vendedor */}
          {isSeller && (
            <div className="flex flex-wrap gap-2">
              {negotiation.status === "pending" && (
                <>
                  <button
                    className="neg-action-btn neg-action-btn--accept"
                    onClick={() => handleAcceptReject("accepted")}
                    disabled={actionLoading}
                  >
                    {actionLoading ? "Procesando…" : "✓ Aceptar Pedido"}
                  </button>
                  <button
                    className="neg-action-btn neg-action-btn--reject"
                    onClick={() => handleAcceptReject("rejected")}
                    disabled={actionLoading}
                  >
                    ✗ Rechazar
                  </button>
                </>
              )}
              {negotiation.status === "accepted" && (
                <button
                  className="neg-action-btn neg-action-btn--pause"
                  onClick={() => handleAcceptReject("paused")}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Procesando…" : "⏸️ Pausar Pedido"}
                </button>
              )}
              {negotiation.status === "paused" && (
                <button
                  className="neg-action-btn neg-action-btn--accept"
                  onClick={() => handleAcceptReject("accepted")}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Procesando…" : "▶️ Reanudar Pedido"}
                </button>
              )}
            </div>
          )}

          {/* Acciones del Comprador */}
          {isBuyer && (
            <div className="flex flex-wrap gap-2">
              {(negotiation.status === "pending" ||
                negotiation.status === "accepted" ||
                negotiation.status === "paused") && (
                <button
                  className="neg-action-btn neg-action-btn--cancel"
                  onClick={() => handleAcceptReject("cancelled")}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Procesando…" : "🚫 Cancelar Pedido"}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Main Content Grid */}
        <div className="neg-detail-grid">
          {/* Chat */}
          <div className="neg-detail-chat">
            {canChat ? (
              <ChatBox negotiationId={negotiationId} />
            ) : (
              <div className="chat-closed">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  opacity="0.4"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p>
                  {negotiation.status === "delivered"
                    ? "Transacción completada. El chat está cerrado."
                    : negotiation.status === "cancelled"
                      ? "Esta negociación fue cancelada. El chat está cerrado."
                      : "Esta negociación fue rechazada. El chat está cerrado."}
                </p>
              </div>
            )}
          </div>

          {/* Sidebar: Payment + Delivery */}
          <div className="neg-detail-sidebar">
            {/* Factura Detallada (HU 8.4) */}
            <NegotiationInvoice
              negotiation={negotiation}
              productName={productName}
            />

            {/* Deep Links de pago (HU 6.2/6.3) */}
            {negotiation.status === "accepted" && isBuyer && (
              <PaymentButtons
                negotiationId={negotiationId}
                disabled={negotiation.status !== "accepted"}
                selectedMethod={negotiation.payment_method}
                onUpdate={(updated) => setNegotiation(updated)}
              />

            )}


            {/* Confirmación de entrega (HU 6.4) */}
            <DeliveryConfirmation
              negotiationId={negotiationId}
              buyerId={negotiation.buyer_id}
              sellerId={negotiation.seller_id}
              buyerConfirmed={negotiation.buyer_confirmed}
              sellerConfirmed={negotiation.seller_confirmed}
              status={negotiation.status}
              onConfirmed={handleDeliveryConfirmed}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
