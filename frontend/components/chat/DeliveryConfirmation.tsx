"use client";

/**
 * DeliveryConfirmation — Botón de confirmación de entrega (HU 6.4).
 *
 * Muestra el estado de confirmación de ambas partes y permite
 * al usuario confirmar su parte de la transacción.
 */

import { useState } from "react";
import { useNegotiations } from "@/hooks/useNegotiations";
import { useAuthStore } from "@/store/authStore";

interface DeliveryConfirmationProps {
  negotiationId: string;
  buyerId: string;
  sellerId: string;
  buyerConfirmed: boolean;
  sellerConfirmed: boolean;
  status: string;
  onConfirmed?: () => void;
}

export default function DeliveryConfirmation({
  negotiationId,
  buyerId,
  sellerId,
  buyerConfirmed,
  sellerConfirmed,
  status,
  onConfirmed,
}: DeliveryConfirmationProps) {
  const { user } = useAuthStore();
  const { confirmDelivery } = useNegotiations();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isBuyer = user?.id === buyerId;
  const isSeller = user?.id === sellerId;
  const myConfirmed = isBuyer ? buyerConfirmed : sellerConfirmed;
  const otherConfirmed = isBuyer ? sellerConfirmed : buyerConfirmed;
  const isCompleted = status === "completed";

  const handleConfirm = async () => {
    setLoading(true);
    setError(null);
    try {
      await confirmDelivery(negotiationId);
      onConfirmed?.();
    } catch (err: any) {
      setError(err.message || "Error al confirmar la entrega");
    } finally {
      setLoading(false);
    }
  };

  if (status !== "accepted" && !isCompleted) return null;

  return (
    <div className={`delivery-confirmation ${isCompleted ? "delivery-confirmation--completed" : ""}`}>
      {isCompleted ? (
        <div className="delivery-completed">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <div>
            <p className="delivery-completed-title">Transacción Completada</p>
            <p className="delivery-completed-text">
              Ambas partes confirmaron la entrega exitosa.
            </p>
          </div>
        </div>
      ) : (
        <>
          <h4 className="delivery-title">Confirmar Entrega</h4>
          <p className="delivery-desc">
            Ambas partes deben confirmar para completar la transacción.
          </p>

          <div className="delivery-status-row">
            <div className={`delivery-check ${buyerConfirmed ? "delivery-check--done" : ""}`}>
              {buyerConfirmed ? "✓" : "○"} Comprador
            </div>
            <div className={`delivery-check ${sellerConfirmed ? "delivery-check--done" : ""}`}>
              {sellerConfirmed ? "✓" : "○"} Vendedor
            </div>
          </div>

          {!myConfirmed && (isBuyer || isSeller) && (
            <button
              className="delivery-btn"
              onClick={handleConfirm}
              disabled={loading}
            >
              {loading ? "Confirmando…" : "✓ Confirmar Entrega"}
            </button>
          )}

          {myConfirmed && !otherConfirmed && (
            <p className="delivery-waiting">
              Esperando confirmación de la otra parte…
            </p>
          )}

          {error && <p className="delivery-error">{error}</p>}
        </>
      )}
    </div>
  );
}
