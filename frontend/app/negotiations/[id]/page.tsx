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
import api from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  pending: "⏳ Pendiente",
  accepted: "✅ Aceptada",
  rejected: "❌ Rechazada",
  completed: "🎉 Completada",
};

export default function NegotiationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const negotiationId = params?.id as string;
  const { user, token, isAuthenticated, isHydrated } = useAuth();
  const { updateStatus } = useNegotiations();

  const [negotiation, setNegotiation] = useState<Negotiation | null>(null);
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
          token
        );
        setNegotiation(data);
      } catch (err: any) {
        setError(err.message || "Error al cargar la negociación");
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [token, negotiationId]);

  const handleAcceptReject = async (status: "accepted" | "rejected") => {
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
        token
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

        {/* Status Banner */}
        <div className={`neg-detail-banner neg-detail-banner--${negotiation.status}`}>
          <div className="neg-detail-banner-left">
            <span className="neg-detail-status">
              {STATUS_LABELS[negotiation.status] || negotiation.status}
            </span>
            <span className="neg-detail-price">
              {formatPrice(negotiation.agreed_price_cop)}
            </span>
          </div>
          <div className="neg-detail-banner-right">
            <span className="neg-detail-role">
              {isBuyer ? "🛒 Eres el Comprador" : "🏪 Eres el Vendedor"}
            </span>
          </div>
        </div>

        {/* Action Buttons (Vendedor: Aceptar/Rechazar) */}
        {isSeller && negotiation.status === "pending" && (
          <div className="neg-actions">
            <button
              className="neg-action-btn neg-action-btn--accept"
              onClick={() => handleAcceptReject("accepted")}
              disabled={actionLoading}
            >
              {actionLoading ? "Procesando…" : "✓ Aceptar Negociación"}
            </button>
            <button
              className="neg-action-btn neg-action-btn--reject"
              onClick={() => handleAcceptReject("rejected")}
              disabled={actionLoading}
            >
              ✗ Rechazar
            </button>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="neg-detail-grid">
          {/* Chat */}
          <div className="neg-detail-chat">
            {canChat ? (
              <ChatBox negotiationId={negotiationId} />
            ) : (
              <div className="chat-closed">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.4">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p>
                  {negotiation.status === "completed"
                    ? "Transacción completada. El chat está cerrado."
                    : "Esta negociación fue rechazada. El chat está cerrado."}
                </p>
              </div>
            )}
          </div>

          {/* Sidebar: Payment + Delivery */}
          <div className="neg-detail-sidebar">
            {/* Deep Links de pago (HU 6.2/6.3) */}
            {negotiation.status === "accepted" && isBuyer && (
              <PaymentButtons
                negotiationId={negotiationId}
                disabled={negotiation.status !== "accepted"}
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
