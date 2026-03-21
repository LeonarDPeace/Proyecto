"use client";

/**
 * Página — Mi Perfil y Configuración de Privacidad (HU 1.2 & HU 1.3).
 *
 * Muestra los datos del usuario autenticado y permite configurar
 * la visibilidad de email y teléfono (Ley 1581/2012).
 */

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import ProductManager from "@/components/products/ProductManager";

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated, isHydrated, updatePrivacy, logout } =
    useAuth();

  /* ── Editable privacy toggles ── */
  const [showEmail, setShowEmail] = useState(false);
  const [showPhone, setShowPhone] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Sync state when user data loads
  useEffect(() => {
    if (user) {
      setShowEmail(user.show_email ?? false);
      setShowPhone(user.show_phone ?? false);
    }
  }, [user]);

  // Redirect unauthenticated users
  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isHydrated, isAuthenticated, router]);

  if (!isHydrated || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Cargando perfil…</p>
      </main>
    );
  }

  async function handleSavePrivacy() {
    setSaving(true);
    setMessage(null);
    try {
      await updatePrivacy({ show_email: showEmail, show_phone: showPhone });
      setMessage("Configuración actualizada correctamente.");
    } catch {
      setMessage("Error al guardar la configuración.");
    } finally {
      setSaving(false);
    }
  }

  function handleLogout() {
    logout();
    router.push("/");
  }

  const hasPrivacyChanges =
    showEmail !== (user.show_email ?? false) ||
    showPhone !== (user.show_phone ?? false);

  const isSeller = user.role === "vendedor";

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Mi Perfil</h1>
        <Button variant="outline" size="sm" onClick={handleLogout}>
          Cerrar sesión
        </Button>
      </div>

      {/* ── Información personal ── */}
      <section className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
        <h2 className="mb-4 text-lg font-semibold text-gray-700">
          Información Personal
        </h2>

        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Nombre"
            value={user.name || "—"}
            disabled
          />
          <Input
            label="Correo institucional"
            value={user.email}
            disabled
          />
          <Input
            label="Código institucional"
            value={user.institutional_id || "—"}
            disabled
          />
          <Input
            label="Teléfono"
            value={user.phone || "No registrado"}
            disabled
          />
          <Input
            label="Rol"
            value={user.role === "vendedor" ? "Vendedor" : "Comprador"}
            disabled
          />
          <Input
            label="Verificado"
            value={user.is_verified ? "Sí" : "Pendiente"}
            disabled
          />
        </div>
      </section>

      {/* ── Configuración de Privacidad (HU 1.3) ── */}
      <section className="mt-6 rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
        <h2 className="mb-2 text-lg font-semibold text-gray-700">
          Privacidad
        </h2>
        <p className="mb-4 text-sm text-gray-500">
          Controla qué información de contacto es visible para otros usuarios.
          Cumplimiento con la Ley 1581/2012 de protección de datos personales.
        </p>

        <div className="space-y-4">
          {/* Toggle: mostrar email */}
          <label className="flex cursor-pointer items-center justify-between rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50">
            <div>
              <p className="font-medium text-gray-700">
                Mostrar correo electrónico
              </p>
              <p className="text-xs text-gray-500">
                Tu email será visible en tu perfil público.
              </p>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={showEmail}
                onChange={(e) => setShowEmail(e.target.checked)}
                className="peer sr-only"
              />
              <div className="h-6 w-11 rounded-full bg-gray-300 transition peer-checked:bg-vera-600"></div>
              <div className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition peer-checked:translate-x-5"></div>
            </div>
          </label>

          {/* Toggle: mostrar teléfono */}
          <label className="flex cursor-pointer items-center justify-between rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50">
            <div>
              <p className="font-medium text-gray-700">
                Mostrar número de teléfono
              </p>
              <p className="text-xs text-gray-500">
                Tu teléfono será visible en tu perfil público.
              </p>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={showPhone}
                onChange={(e) => setShowPhone(e.target.checked)}
                className="peer sr-only"
              />
              <div className="h-6 w-11 rounded-full bg-gray-300 transition peer-checked:bg-vera-600"></div>
              <div className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition peer-checked:translate-x-5"></div>
            </div>
          </label>
        </div>

        {message && (
          <p
            className={`mt-4 text-sm ${
              message.startsWith("Error") ? "text-red-600" : "text-green-600"
            }`}
          >
            {message}
          </p>
        )}

        <Button
          variant="primary"
          size="md"
          className="mt-4 w-full sm:w-auto"
          onClick={handleSavePrivacy}
          disabled={saving || !hasPrivacyChanges}
        >
          {saving ? "Guardando…" : "Guardar privacidad"}
        </Button>
      </section>

      {/* ── Mis Productos (Sprint 3 — Solo vendedores) ── */}
      {isSeller && (
        <section className="mt-6 rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-700">
              Mis Productos
            </h2>
            <Link
              href="/products/new"
              className="inline-flex items-center gap-1 text-sm font-medium text-vera-600 hover:underline"
            >
              + Publicar nuevo
            </Link>
          </div>
          <ProductManager />
        </section>
      )}

      {/* Footer */}
      <footer className="mt-8 text-center text-xs text-gray-400">
        <p>
          Tus datos se gestionan conforme a la Ley 1581/2012.
        </p>
      </footer>
    </main>
  );
}
