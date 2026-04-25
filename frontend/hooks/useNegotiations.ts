"use client";

/**
 * Hook — useNegotiations: gestión de negociaciones P2P (Sprint 4).
 *
 * HU 6.1: Chat interno en tiempo real.
 * HU 6.4: Confirmación de entrega.
 */

import { useState, useCallback } from "react";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export interface Negotiation {
  id: string;
  buyer_id: string;
  seller_id: string;
  product_id: string;
  status: "pending" | "accepted" | "rejected" | "completed";
  buyer_confirmed: boolean;
  seller_confirmed: boolean;
  agreed_price_cop: number | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  negotiation_id: string;
  sender_id: string;
  content: string;
  created_at: string;
}

export interface PaymentDeepLink {
  platform: "nequi" | "daviplata";
  deep_link_url: string;
  seller_phone: string;
  amount_cop: number | null;
  message: string;
}

export function useNegotiations() {
  const { token } = useAuthStore();
  const [negotiations, setNegotiations] = useState<Negotiation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Lista todas las negociaciones del usuario autenticado */
  const fetchNegotiations = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Negotiation[]>("/negotiations/", token);
      setNegotiations(data);
    } catch (err: any) {
      setError(err.message || "Error al cargar negociaciones");
    } finally {
      setLoading(false);
    }
  }, [token]);

  /** Inicia una nueva negociación */
  const createNegotiation = useCallback(
    async (productId: string, initialMessage?: string) => {
      if (!token) throw new Error("No autenticado");
      const data = await api.post<Negotiation>(
        "/negotiations/",
        { product_id: productId, initial_message: initialMessage },
        token
      );
      setNegotiations((prev) => [data, ...prev]);
      return data;
    },
    [token]
  );

  /** Actualiza el estado de una negociación (aceptar/rechazar) */
  const updateStatus = useCallback(
    async (negotiationId: string, status: "accepted" | "rejected") => {
      if (!token) throw new Error("No autenticado");
      const data = await api.patch<Negotiation>(
        `/negotiations/${negotiationId}/status`,
        { status },
        token
      );
      setNegotiations((prev) =>
        prev.map((n) => (n.id === negotiationId ? data : n))
      );
      return data;
    },
    [token]
  );

  /** Confirma entrega (HU 6.4) */
  const confirmDelivery = useCallback(
    async (negotiationId: string) => {
      if (!token) throw new Error("No autenticado");
      const data = await api.patch<Negotiation>(
        `/negotiations/${negotiationId}/confirm`,
        {},
        token
      );
      setNegotiations((prev) =>
        prev.map((n) => (n.id === negotiationId ? data : n))
      );
      return data;
    },
    [token]
  );

  /** Obtiene mensajes del chat */
  const fetchMessages = useCallback(
    async (negotiationId: string) => {
      if (!token) throw new Error("No autenticado");
      return api.get<ChatMessage[]>(
        `/negotiations/${negotiationId}/messages`,
        token
      );
    },
    [token]
  );

  /** Envía un mensaje en el chat */
  const sendMessage = useCallback(
    async (negotiationId: string, content: string) => {
      if (!token) throw new Error("No autenticado");
      return api.post<ChatMessage>(
        `/negotiations/${negotiationId}/messages`,
        { content },
        token
      );
    },
    [token]
  );

  /** Genera deep link de pago (HU 6.2/6.3) */
  const getPaymentLink = useCallback(
    async (negotiationId: string, platform: "nequi" | "daviplata") => {
      if (!token) throw new Error("No autenticado");
      return api.get<PaymentDeepLink>(
        `/negotiations/${negotiationId}/payment-link?platform=${platform}`,
        token
      );
    },
    [token]
  );

  return {
    negotiations,
    loading,
    error,
    fetchNegotiations,
    createNegotiation,
    updateStatus,
    confirmDelivery,
    fetchMessages,
    sendMessage,
    getPaymentLink,
  };
}
