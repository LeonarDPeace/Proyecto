"use client";

import { useMemo } from "react";

interface OrderTimelineProps {
  status: "pending" | "accepted" | "paused" | "rejected" | "cancelled" | "delivered";
}

const STEPS = [
  { key: "pending", label: "Pendiente", icon: "⏳" },
  { key: "accepted", label: "Aceptado", icon: "✅" },
  { key: "delivered", label: "Entregado", icon: "📦" },
];

export default function OrderTimeline({ status }: OrderTimelineProps) {
  // Determinar el progreso basado en el estado
  // Si está rechazado o cancelado, mostramos un estado especial
  const isTerminalNegative = status === "rejected" || status === "cancelled";
  
  const currentStepIndex = useMemo(() => {
    if (status === "pending") return 0;
    if (status === "accepted" || status === "paused") return 1;
    if (status === "delivered") return 2;
    return -1;
  }, [status]);

  return (
    <div className="order-timeline-container">
      <div className="order-timeline">
        {STEPS.map((step, index) => {
          const isCompleted = index <= currentStepIndex;
          const isCurrent = index === currentStepIndex;
          const isPaused = isCurrent && status === "paused";

          return (
            <div key={step.key} className="timeline-step">
              <div className={`step-circle ${isCompleted ? "completed" : ""} ${isCurrent ? "current" : ""} ${isPaused ? "paused" : ""}`}>
                {step.icon}
              </div>
              <div className="step-label">{step.label}</div>
              {index < STEPS.length - 1 && (
                <div className={`step-line ${index < currentStepIndex ? "completed" : ""}`} />
              )}
            </div>
          );
        })}
      </div>

      {isTerminalNegative && (
        <div className="timeline-negative-status">
          <span className="icon">⚠️</span>
          <span className="text">
            Este pedido ha sido {status === "rejected" ? "rechazado por el vendedor" : "cancelado"}.
          </span>
        </div>
      )}
      
      {status === "paused" && (
        <div className="timeline-info-status">
          <span className="icon">⏸️</span>
          <span className="text">El vendedor ha pausado este pedido temporalmente.</span>
        </div>
      )}
    </div>
  );
}
