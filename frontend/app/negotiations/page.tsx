"use client";

/**
 * Negotiations Page — Lista de negociaciones del usuario (Sprint 4).
 *
 * Muestra todas las negociaciones del usuario autenticado con filtros por estado.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useNegotiations, Negotiation } from "@/hooks/useNegotiations";

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  pending: { label: "Pendiente", color: "#f59e0b" },
  accepted: { label: "Aceptada", color: "#10b981" },
  rejected: { label: "Rechazada", color: "#ef4444" },
  completed: { label: "Completada", color: "#6366f1" },
};

export default function NegotiationsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isHydrated } = useAuth();
  const { negotiations, loading, error, fetchNegotiations } = useNegotiations();
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isHydrated, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchNegotiations();
    }
  }, [isAuthenticated, fetchNegotiations]);

  const filteredNegotiations =
    filter === "all"
      ? negotiations
      : negotiations.filter((n) => n.status === filter);

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("es-CO", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatPrice = (price: number | null) => {
    if (!price) return "—";
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (!isHydrated) {
    return (
      <main className="neg-page">
        <div className="neg-loading">
          <div className="neg-loading-spinner" />
        </div>
      </main>
    );
  }

  return (
    <main className="neg-page">
      <div className="neg-container">
        {/* Header */}
        <div className="neg-header">
          <h1 className="neg-title">Mis Negociaciones</h1>
          <p className="neg-subtitle">
            {user?.role === "vendedor"
              ? "Gestiona las ofertas y mensajes de tus compradores."
              : "Sigue el estado de tus compras y mensajes con vendedores."}
          </p>
        </div>

        {/* Filtros */}
        <div className="neg-filters">
          {["all", "pending", "accepted", "completed", "rejected"].map((s) => (
            <button
              key={s}
              className={`neg-filter-btn ${filter === s ? "neg-filter-btn--active" : ""}`}
              onClick={() => setFilter(s)}
            >
              {s === "all" ? "Todas" : STATUS_LABELS[s]?.label || s}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && <div className="neg-error">{error}</div>}

        {/* Loading */}
        {loading && (
          <div className="neg-loading">
            <div className="neg-loading-spinner" />
            <span>Cargando negociaciones…</span>
          </div>
        )}

        {/* Lista vacía */}
        {!loading && filteredNegotiations.length === 0 && (
          <div className="neg-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.4">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>No tienes negociaciones {filter !== "all" ? `con estado "${STATUS_LABELS[filter]?.label}"` : "aún"}.</p>
            {filter === "all" && (
              <button
                className="neg-browse-btn"
                onClick={() => router.push("/products")}
              >
                Explorar Productos
              </button>
            )}
          </div>
        )}

        {/* Lista de negociaciones */}
        <div className="neg-list">
          {filteredNegotiations.map((neg: Negotiation) => {
            const statusInfo = STATUS_LABELS[neg.status] || {
              label: neg.status,
              color: "#94a3b8",
            };
            const isMyBuy = neg.buyer_id === user?.id;

            return (
              <div
                key={neg.id}
                className="neg-card"
                onClick={() => router.push(`/negotiations/${neg.id}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter") router.push(`/negotiations/${neg.id}`);
                }}
              >
                <div className="neg-card-top">
                  <span
                    className="neg-card-badge"
                    style={{ backgroundColor: statusInfo.color + "20", color: statusInfo.color }}
                  >
                    {statusInfo.label}
                  </span>
                  <span className="neg-card-role">
                    {isMyBuy ? "🛒 Compra" : "🏪 Venta"}
                  </span>
                </div>

                <div className="neg-card-body">
                  <p className="neg-card-price">{formatPrice(neg.agreed_price_cop)}</p>
                  <p className="neg-card-date">{formatDate(neg.updated_at)}</p>
                </div>

                <div className="neg-card-footer">
                  {neg.status === "accepted" && (
                    <div className="neg-card-confirmations">
                      <span className={neg.buyer_confirmed ? "confirmed" : ""}>
                        {neg.buyer_confirmed ? "✓" : "○"} Comprador
                      </span>
                      <span className={neg.seller_confirmed ? "confirmed" : ""}>
                        {neg.seller_confirmed ? "✓" : "○"} Vendedor
                      </span>
                    </div>
                  )}
                  <span className="neg-card-arrow">→</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}
