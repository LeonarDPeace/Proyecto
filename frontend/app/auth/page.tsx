"use client";

/**
 * Página de autenticación — Flujo OTP (HU 1.1).
 *
 * Paso 1: El usuario ingresa su correo institucional (.edu.co).
 * Paso 2: Ingresa el código OTP recibido en su correo.
 * Paso 3: Si es nuevo, se redirige a completar perfil.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

type Step = "email" | "otp";

export default function AuthPage() {
  const router = useRouter();
  const { requestOTP, verifyOTP } = useAuth();

  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [expiresIn, setExpiresIn] = useState(10);

  // --- Paso 1: Solicitar OTP ---
  async function handleRequestOTP(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!email.trim().toLowerCase().endsWith(".edu.co")) {
      setError("Solo se permiten correos institucionales (.edu.co)");
      return;
    }

    setLoading(true);
    try {
      const response = await requestOTP(email.trim().toLowerCase());
      setExpiresIn(response.expires_in_minutes);
      setStep("otp");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al enviar código");
    } finally {
      setLoading(false);
    }
  }

  // --- Paso 2: Verificar OTP ---
  async function handleVerifyOTP(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (code.length !== 6) {
      setError("El código debe tener 6 dígitos");
      return;
    }

    setLoading(true);
    try {
      const response = await verifyOTP(email, code);
      if (response.is_new_user) {
        router.push("/profile/complete");
      } else {
        router.push("/products");
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "Código inválido o expirado"
      );
    } finally {
      setLoading(false);
    }
  }

  // --- Reenviar OTP ---
  async function handleResendOTP() {
    setError(null);
    setCode("");
    setLoading(true);
    try {
      await requestOTP(email);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al reenviar código");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
        {/* Logo */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-vera-700">
            Vera<span className="text-vera-500">Market</span>
          </h1>
          <p className="mt-2 text-sm text-gray-500">
            Marketplace universitario — Campus UAO
          </p>
        </div>

        {/* Step 1: Email */}
        {step === "email" && (
          <form onSubmit={handleRequestOTP} className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">
                Iniciar sesión
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Ingresa tu correo institucional (.edu.co) y te enviaremos un
                código de acceso.
              </p>
            </div>

            <Input
              label="Correo institucional"
              type="email"
              placeholder="tu.nombre@uao.edu.co"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={error || undefined}
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={loading || !email.trim()}
            >
              {loading ? "Enviando..." : "Enviar código"}
            </Button>
          </form>
        )}

        {/* Step 2: OTP Code */}
        {step === "otp" && (
          <form onSubmit={handleVerifyOTP} className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-800">
                Verificar código
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Enviamos un código de 6 dígitos a{" "}
                <span className="font-medium text-vera-600">{email}</span>.
                Expira en {expiresIn} minutos.
              </p>
            </div>

            <Input
              label="Código OTP"
              type="text"
              placeholder="000000"
              value={code}
              onChange={(e) => {
                const v = e.target.value.replace(/\D/g, "").slice(0, 6);
                setCode(v);
              }}
              error={error || undefined}
              maxLength={6}
              required
              autoFocus
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={loading || code.length !== 6}
            >
              {loading ? "Verificando..." : "Verificar"}
            </Button>

            <div className="flex items-center justify-between text-sm">
              <button
                type="button"
                onClick={() => {
                  setStep("email");
                  setCode("");
                  setError(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ← Cambiar correo
              </button>
              <button
                type="button"
                onClick={handleResendOTP}
                disabled={loading}
                className="text-vera-600 hover:text-vera-700 font-medium"
              >
                Reenviar código
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-gray-400">
          Al iniciar sesión aceptas los{" "}
          <a href="#" className="text-vera-600 hover:underline">
            Términos y Condiciones
          </a>{" "}
          (Ley 1581/2012)
        </p>
      </div>
    </main>
  );
}
