"use client";

import { useState } from "react";
import Button from "./ui/Button";
import Input from "./ui/Input";
import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId?: string;
  reportedUserId?: string;
  targetName: string;
}

export default function ReportModal({
  isOpen,
  onClose,
  productId,
  reportedUserId,
  targetName,
}: ReportModalProps) {
  const { token, isAuthenticated } = useAuth();
  const [reason, setReason] = useState<"spam" | "offensive" | "fraud">("spam");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isAuthenticated) {
      setError("Debes iniciar sesión para reportar.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await api.post("/reports/", {
        product_id: productId || null,
        reported_user_id: reportedUserId || null,
        reason,
        description: description.trim() || null,
      }, token || undefined);

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Error al enviar el reporte");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          Denunciar {productId ? "Publicación" : "Usuario"}
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Estás reportando a: <span className="font-semibold text-gray-700">{targetName}</span>
        </p>

        {success ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">✅</div>
            <p className="text-green-600 font-medium">Gracias por tu reporte. Lo revisaremos pronto.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ¿Por qué quieres denunciar?
              </label>
              <select
                className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-vera-500 focus:ring-vera-500 outline-none"
                value={reason}
                onChange={(e) => setReason(e.target.value as any)}
                required
              >
                <option value="spam">Spam / Publicidad engañosa</option>
                <option value="offensive">Comportamiento ofensivo / Lenguaje inapropiado</option>
                <option value="fraud">Posible fraude o estafa</option>
              </select>
            </div>

            <Input
              label="Descripción (opcional)"
              type="text"
              placeholder="Cuéntanos un poco más..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={500}
            />

            {error && <p className="text-xs text-red-600">{error}</p>}

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={onClose}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="primary"
                className="flex-1 bg-red-600 hover:bg-red-700 border-none"
                disabled={loading}
              >
                {loading ? "Enviando..." : "Enviar Denuncia"}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
