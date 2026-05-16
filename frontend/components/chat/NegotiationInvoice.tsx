"use client";

import { Negotiation } from "@/hooks/useNegotiations";

interface NegotiationInvoiceProps {
  negotiation: Negotiation;
  productName: string;
}

export default function NegotiationInvoice({ negotiation, productName }: NegotiationInvoiceProps) {
  const unitPrice = negotiation.agreed_price_cop || 0;
  const quantity = negotiation.quantity || 1;
  const subtotal = unitPrice * quantity;
  const discount = negotiation.discount_amount || 0; 
  const total = subtotal - discount;


  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="negotiation-invoice">
      <h3 className="invoice-title">Recibo de Pedido</h3>
      
      <div className="invoice-details">
        <div className="invoice-row">
          <span className="label">Producto:</span>
          <span className="value">{productName}</span>
        </div>
        <div className="invoice-row">
          <span className="label">Cantidad:</span>
          <span className="value">x{quantity}</span>
        </div>
        <div className="invoice-row">
          <span className="label">Precio Unitario:</span>
          <span className="value">{formatPrice(unitPrice)}</span>
        </div>
      </div>

      <div className="invoice-divider" />

      <div className="invoice-totals">
        <div className="invoice-row">
          <span className="label">Subtotal:</span>
          <span className="value">{formatPrice(subtotal)}</span>
        </div>
        {discount > 0 && (
          <div className="invoice-row discount">
            <span className="label">Descuento:</span>
            <span className="value">-{formatPrice(discount)}</span>
          </div>
        )}
        <div className="invoice-row total">
          <span className="label">Total a Pagar:</span>
          <span className="value">{formatPrice(total)}</span>
        </div>
      </div>

      {negotiation.payment_method && (
        <div className="invoice-method">
          <span className="badge">Pago: {negotiation.payment_method}</span>
        </div>
      )}
    </div>
  );
}
