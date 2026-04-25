"use client";

/**
 * ChatBox — Componente de chat en tiempo real (Sprint 4 — HU 6.1).
 *
 * Muestra mensajes en tiempo real usando WebSocket.
 * Permite enviar mensajes y muestra el estado de conexión.
 */

import { useState, useEffect, useRef } from "react";
import { useChat, WsMessage } from "@/hooks/useChat";
import { useNegotiations, ChatMessage } from "@/hooks/useNegotiations";
import { useAuthStore } from "@/store/authStore";

interface ChatBoxProps {
  negotiationId: string;
}

export default function ChatBox({ negotiationId }: ChatBoxProps) {
  const { user } = useAuthStore();
  const { fetchMessages } = useNegotiations();
  const {
    messages: wsMessages,
    setMessages,
    connected,
    connecting,
    sendMessage,
  } = useChat({ negotiationId });

  const [inputValue, setInputValue] = useState("");
  const [loadingHistory, setLoadingHistory] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Cargar historial de mensajes al montar
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await fetchMessages(negotiationId);
        const formatted: WsMessage[] = history.map((m: ChatMessage) => ({
          type: "message" as const,
          id: m.id,
          negotiation_id: m.negotiation_id,
          sender_id: m.sender_id,
          content: m.content,
          created_at: m.created_at,
        }));
        setMessages(formatted);
      } catch {
        console.error("Error loading chat history");
      } finally {
        setLoadingHistory(false);
      }
    };
    loadHistory();
  }, [negotiationId, fetchMessages, setMessages]);

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [wsMessages]);

  const { sendMessage: sendViaRest } = useNegotiations();

  const handleSend = async () => {
    const content = inputValue.trim();
    if (!content) return;
    
    // Guardamos el input para limpiar después
    setInputValue("");
    
    try {
      // Usamos REST para máxima fiabilidad en el envío
      await sendViaRest(negotiationId, content);
      // El mensaje aparecerá en la pantalla vía WebSocket (el servidor lo retransmitirá)
    } catch (err: any) {
      console.error("Error al enviar mensaje:", err);
      // Opcional: restaurar el input si falló
      setInputValue(content);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="chat-box">
      {/* Header con estado de conexión */}
      <div className="chat-header">
        <div className="chat-header-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span>Chat</span>
        </div>
        <div className={`chat-status ${connected ? "chat-status--online" : "chat-status--offline"}`}>
          <span className="chat-status-dot" />
          {connecting ? "Conectando…" : connected ? "En línea" : "Desconectado"}
        </div>
      </div>

      {/* Mensajes */}
      <div className="chat-messages">
        {loadingHistory && (
          <div className="chat-loading">
            <div className="chat-loading-spinner" />
            <span>Cargando historial…</span>
          </div>
        )}

        {wsMessages.map((msg, i) => {
          if (msg.type === "system") {
            return (
              <div key={`sys-${i}`} className="chat-system-msg">
                {msg.content}
              </div>
            );
          }

          if (msg.type === "error") {
            return (
              <div key={`err-${i}`} className="chat-error-msg">
                ⚠️ {msg.content}
              </div>
            );
          }

          const isOwn = msg.sender_id === user?.id;
          return (
            <div
              key={msg.id || `msg-${i}`}
              className={`chat-bubble ${isOwn ? "chat-bubble--own" : "chat-bubble--other"}`}
            >
              {!isOwn && msg.sender_name && (
                <span className="chat-bubble-name">{msg.sender_name}</span>
              )}
              <p className="chat-bubble-content">{msg.content}</p>
              <span className="chat-bubble-time">{formatTime(msg.created_at)}</span>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Escribe un mensaje…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          maxLength={2000}
        />
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={!inputValue.trim()}
          aria-label="Enviar mensaje"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}
