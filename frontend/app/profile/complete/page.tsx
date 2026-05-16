"use client";

/**
 * Página — Completar Perfil (HU 1.2).
 *
 * Se muestra tras el primer login OTP cuando is_new_user === true.
 * El usuario debe completar nombre, código institucional y aceptar T&C.
 * Rol por defecto: Comprador.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

export default function CompleteProfilePage() {
  const router = useRouter();
  const { completeProfile, isAuthenticated, isNewUser } = useAuth();

  const [name, setName] = useState("");
  const [institutionalId, setInstitutionalId] = useState("");
  const [phone, setPhone] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Redirect if not authenticated or not a new user
  if (typeof window !== "undefined" && !isAuthenticated) {
    router.push("/auth");
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!acceptTerms) {
      setError("Debe aceptar los términos y condiciones (Ley 1581/2012)");
      return;
    }

    if (name.trim().length < 2) {
      setError("El nombre debe tener al menos 2 caracteres");
      return;
    }

    if (!institutionalId.trim()) {
      setError("El código institucional es obligatorio");
      return;
    }

    setLoading(true);
    try {
      await completeProfile({
        name: name.trim(),
        institutional_id: institutionalId.trim(),
        phone: phone.trim() || undefined,
        accept_terms: acceptTerms,
      });
      router.push("/products");
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Error al completar perfil",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-800">
            Completa tu perfil
          </h1>
          <p className="mt-2 text-sm text-gray-500">
            Necesitamos algunos datos para activar tu cuenta en VeraMarket. Tu
            rol por defecto será <strong>Comprador</strong>.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nombre completo"
            type="text"
            placeholder="Tu nombre completo"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            minLength={2}
            maxLength={150}
          />

          <Input
            label="Código institucional"
            type="text"
            placeholder="Ej: 2210001"
            value={institutionalId}
            onChange={(e) => setInstitutionalId(e.target.value)}
            required
            maxLength={50}
          />

          <Input
            label="Teléfono (opcional)"
            type="tel"
            placeholder="3001234567"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            maxLength={20}
          />

          {/* Aceptación de términos — Ley 1581/2012 */}
          <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <input
              type="checkbox"
              id="accept-terms"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-vera-600 focus:ring-vera-500"
            />
            <label htmlFor="accept-terms" className="text-sm text-gray-600">
              Acepto los{" "}
              <a href="#" className="font-medium text-vera-600 hover:underline">
                Términos y Condiciones
              </a>{" "}
              y la{" "}
              <a href="#" className="font-medium text-vera-600 hover:underline">
                Política de Tratamiento de Datos
              </a>{" "}
              (Ley 1581/2012).
            </label>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            disabled={
              loading || !acceptTerms || !name.trim() || !institutionalId.trim()
            }
          >
            {loading ? "Guardando..." : "Completar registro"}
          </Button>
        </form>
      </div>
    </main>
  );
}
