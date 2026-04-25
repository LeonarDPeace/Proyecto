"use client";

/**
 * PaymentButtons — Botones de Deep Link para Nequi y DaviPlata (HU 6.2/6.3).
 *
 * RESTRICCIÓN: NO hay integración con APIs bancarias.
 * Solo genera Deep Links / URI Schemes que intentan abrir la app en el dispositivo.
 */

import { useState } from "react";
import { useNegotiations } from "@/hooks/useNegotiations";

interface PaymentButtonsProps {
  negotiationId: string;
  disabled?: boolean;
}

export default function PaymentButtons({
  negotiationId,
  disabled = false,
}: PaymentButtonsProps) {
  const { getPaymentLink } = useNegotiations();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [demoMessage, setDemoMessage] = useState<{ platform: string, link: string } | null>(null);

  const handlePayment = async (platform: "nequi" | "daviplata") => {
    setLoading(platform);
    setError(null);
    setDemoMessage(null);
    try {
      const link = await getPaymentLink(negotiationId, platform);

      // Mostrar el mensaje de modo demo con la información obtenida
      setDemoMessage({
        platform: platform === "nequi" ? "Nequi" : "DaviPlata",
        link: link.deep_link_url
      });

      // Detectar si es un dispositivo móvil para intentar abrir el Deep Link
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      if (isMobile) {
        window.location.href = link.deep_link_url;
      }
      
      setLoading(null);
    } catch (err: any) {
      setError(err.message || `Error generando enlace de ${platform}`);
      setLoading(null);
    }
  };

  return (
    <div className="payment-buttons">
      <p className="payment-buttons-label">Pagar con:</p>
      <div className="payment-buttons-row">
        {/* Nequi */}
        <button
          className="payment-btn payment-btn--nequi"
          onClick={() => handlePayment("nequi")}
          disabled={disabled || loading === "nequi"}
          aria-label="Pagar con Nequi"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10" opacity="0.2" />
            <text x="12" y="16" textAnchor="middle" fontSize="10" fontWeight="bold" fill="currentColor">N</text>
          </svg>
          {loading === "nequi" ? "Procesando…" : "Nequi"}
        </button>

        {/* DaviPlata */}
        <button
          className="payment-btn payment-btn--daviplata"
          onClick={() => handlePayment("daviplata")}
          disabled={disabled || loading === "daviplata"}
          aria-label="Pagar con DaviPlata"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10" opacity="0.2" />
            <text x="12" y="16" textAnchor="middle" fontSize="10" fontWeight="bold" fill="currentColor">D</text>
          </svg>
          {loading === "daviplata" ? "Procesando…" : "DaviPlata"}
        </button>
      </div>

      {error && <p className="payment-error">{error}</p>}

      {/* Mensaje de Modo Demo para el Sprint 4 */}
      {demoMessage && (
        <div className="payment-demo-message" style={{
          marginTop: "12px",
          padding: "12px",
          backgroundColor: "rgba(255, 193, 7, 0.15)",
          borderLeft: "4px solid #ffc107",
          borderRadius: "4px",
          fontSize: "0.85rem",
          color: "#b28600"
        }}>
          <strong>Modo Demo (Sprint 4):</strong> Las integraciones bancarias directas están deshabilitadas. 
          En un entorno de producción móvil, esta acción abriría automáticamente la aplicación de <strong>{demoMessage.platform}</strong> con el siguiente enlace de pago autogenerado:
          <br /><br />
          <code style={{ background: "rgba(0,0,0,0.05)", padding: "4px", borderRadius: "4px", wordBreak: "break-all" }}>
            {demoMessage.link}
          </code>
        </div>
      )}

      {!demoMessage && (
        <p className="payment-disclaimer">
          Se abrirá la aplicación de pago en tu dispositivo. No almacenamos datos bancarios.
        </p>
      )}
    </div>
  );
}
