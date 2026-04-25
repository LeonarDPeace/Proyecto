"use client";

/**
 * Hook — useChat: WebSocket para chat en tiempo real (Sprint 4 — HU 6.1).
 *
 * Maneja la conexión WebSocket, reconexión automática, y estado de mensajes.
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "@/store/authStore";

export interface WsMessage {
  type: "message" | "system" | "error";
  id?: string;
  negotiation_id?: string;
  sender_id?: string;
  sender_name?: string;
  content: string;
  created_at?: string;
}

interface UseChatOptions {
  negotiationId: string;
  enabled?: boolean;
}

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:8000`
    : "ws://localhost:8000");

export function useChat({ negotiationId, enabled = true }: UseChatOptions) {
  const { token } = useAuthStore();
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!token || !negotiationId || !enabled) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnecting(true);

    const ws = new WebSocket(
      `${WS_BASE_URL}/ws/chat/${negotiationId}?token=${token}`
    );

    ws.onopen = () => {
      setConnected(true);
      setConnecting(false);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev, msg]);
      } catch {
        console.error("Error parsing WS message");
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setConnecting(false);
      wsRef.current = null;

      // Auto-reconexión con backoff exponencial
      if (enabled && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(
          1000 * Math.pow(2, reconnectAttempts.current),
          30000
        );
        reconnectAttempts.current++;
        reconnectTimerRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [token, negotiationId, enabled]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    reconnectAttempts.current = maxReconnectAttempts; // Prevent reconnect
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
    setConnecting(false);
  }, []);

  const sendMessage = useCallback(
    (content: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ content }));
      }
    },
    []
  );

  // Conectar al montar, desconectar al desmontar
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    messages,
    setMessages,
    connected,
    connecting,
    sendMessage,
    connect,
    disconnect,
  };
}
