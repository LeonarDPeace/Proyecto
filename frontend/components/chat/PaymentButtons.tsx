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
  selectedMethod?: string | null;
  onUpdate?: (negotiation: any) => void;
}


export default function PaymentButtons({
  negotiationId,
  disabled = false,
  selectedMethod = null,
  onUpdate,
}: PaymentButtonsProps) {

  const { getPaymentLink, setPaymentMethod } = useNegotiations();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isChanging, setIsChanging] = useState(false);
  const [couponCode, setCouponCode] = useState("");
  const [demoMessage, setDemoMessage] = useState<{
    platform: string;
    link: string;
  } | null>(null);

  const handlePayment = async (platform: "nequi" | "daviplata") => {
    setLoading(platform);
    setError(null);
    setDemoMessage(null);
    try {
      const updated = await setPaymentMethod(negotiationId, platform, couponCode || null);
      onUpdate?.(updated);
      
      const link = await getPaymentLink(negotiationId, platform);
      setDemoMessage({
        platform: platform === "nequi" ? "Nequi" : "DaviPlata",
        link: link.deep_link_url,
      });

      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      if (isMobile) {
        window.location.href = link.deep_link_url;
      }
      setLoading(null);
      setIsChanging(false);
    } catch (err: any) {
      setError(err.message || `Error generando enlace de ${platform}`);
      setLoading(null);
    }
  };

  const handleCashPayment = async () => {
    setLoading("efectivo");
    setError(null);
    setDemoMessage(null);
    try {
      const updated = await setPaymentMethod(negotiationId, "efectivo", couponCode || null);
      onUpdate?.(updated);

      setDemoMessage({
        platform: "Efectivo",
        link: "Coordinado. Acuerda el punto de encuentro con el vendedor por el chat.",
      });

      setLoading(null);
      setIsChanging(false);
    } catch (err: any) {
      setError(err.message || "Error al seleccionar pago en efectivo");
      setLoading(null);
    }
  };

  const showTransfer = isChanging || !selectedMethod || (selectedMethod !== "efectivo");
  const showCash = isChanging || !selectedMethod || (selectedMethod === "efectivo");


  return (
    <div className="payment-buttons">
      {/* Sistema de Cupones (HU 8.9) */}
      {(!selectedMethod || isChanging) && (
        <div className="mb-4">
          <label htmlFor="coupon" className="block text-[11px] font-bold text-gray-500 uppercase mb-1">
            ¿Tienes un cupón?
          </label>
          <div className="flex gap-2">
            <input
              id="coupon"
              type="text"
              placeholder="CÓDIGO10"
              className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-vera-500"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-2">
        <p className="payment-buttons-label">Método de pago:</p>
        {selectedMethod && !isChanging && (
          <button 
            onClick={() => setIsChanging(true)}
            className="text-[10px] font-bold text-vera-600 hover:underline uppercase tracking-wider"
          >
            Cambiar
          </button>
        )}
      </div>

      <div className="payment-buttons-row">
        {/* Nequi */}
        {showTransfer && (
          <button
            className={`payment-btn payment-btn--nequi ${selectedMethod === "nequi" ? "ring-2 ring-vera-500" : ""}`}
            onClick={() => handlePayment("nequi")}
            disabled={disabled || loading !== null}
            aria-label="Pagar con Nequi"
          >
            <span className="payment-icon">N</span>
            {loading === "nequi" ? "…" : "Nequi"}
          </button>
        )}

        {/* DaviPlata */}
        {showTransfer && (
          <button
            className={`payment-btn payment-btn--daviplata ${selectedMethod === "daviplata" ? "ring-2 ring-vera-500" : ""}`}
            onClick={() => handlePayment("daviplata")}
            disabled={disabled || loading !== null}
            aria-label="Pagar con DaviPlata"
          >
            <span className="payment-icon">D</span>
            {loading === "daviplata" ? "…" : "DaviPlata"}
          </button>
        )}

        {/* Efectivo (HU 8.4) */}
        {showCash && (
          <button
            className={`payment-btn payment-btn--cash ${selectedMethod === "efectivo" ? "ring-2 ring-vera-500" : ""}`}
            onClick={handleCashPayment}
            disabled={disabled || loading !== null}
            aria-label="Pagar en Efectivo"
          >
            <span className="payment-icon">💵</span>
            {loading === "efectivo" ? "…" : "Efectivo"}
          </button>
        )}
      </div>



      {error && <p className="payment-error">{error}</p>}

      {/* Mensaje de Modo Demo para el Sprint 4 */}
      {demoMessage && (
        <div
          className="payment-demo-message"
          style={{
            marginTop: "12px",
            padding: "12px",
            backgroundColor: "rgba(255, 193, 7, 0.15)",
            borderLeft: "4px solid #ffc107",
            borderRadius: "4px",
            fontSize: "0.85rem",
            color: "#b28600",
          }}
        >
          <strong>{demoMessage.platform === "Efectivo" ? "Pago en Efectivo Seleccionado" : "Modo Demo (Sprint 4):"}</strong> 
          {demoMessage.platform === "Efectivo" ? (
            <p className="mt-1">{demoMessage.link}</p>
          ) : (
            <>
              <p className="mt-1">
                En un entorno móvil, esta acción abriría automáticamente la aplicación de{" "}
                <strong>{demoMessage.platform}</strong> con el siguiente enlace de pago:
              </p>
              <br />
              <code
                style={{
                  background: "rgba(0,0,0,0.05)",
                  padding: "4px",
                  borderRadius: "4px",
                  wordBreak: "break-all",
                }}
              >
                {demoMessage.link}
              </code>
            </>
          )}
        </div>
      )}


      {!demoMessage && (
        <p className="payment-disclaimer">
          Se abrirá la aplicación de pago en tu dispositivo. No almacenamos
          datos bancarios.
        </p>
      )}
    </div>
  );
}
