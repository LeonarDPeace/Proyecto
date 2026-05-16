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
import api from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import MapView from "@/components/MapView";
import ProductManager from "@/components/products/ProductManager";
import CouponManager from "@/components/coupons/CouponManager";

interface SavedLocation {
  id: string;
  user_id: string;
  campus: string;
  label: string | null;
  lat: number;
  lng: number;
}

const DEFAULT_LAT = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_LAT || "3.3516");
const DEFAULT_LNG = parseFloat(
  process.env.NEXT_PUBLIC_DEFAULT_LNG || "-76.5320",
);

export default function ProfilePage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isHydrated, updatePrivacy, updateProfile, logout, switchRole, toggleViewMode, viewMode } =
    useAuth();

  /* ── Editable privacy toggles ── */
  const [showEmail, setShowEmail] = useState(false);
  const [showPhone, setShowPhone] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  /* ── Seller location setup ── */
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationSaving, setLocationSaving] = useState(false);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);
  const [locationCampus, setLocationCampus] = useState("UAO");
  const [locationLabel, setLocationLabel] = useState("");
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);

  // Profile Edit State
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editName, setEditName] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [profileSaving, setProfileSaving] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

  // Sync state when user data loads
  useEffect(() => {
    if (user) {
      setShowEmail(user.show_email ?? false);
      setShowPhone(user.show_phone ?? false);
      setEditName(user.name ?? "");
      setEditPhone(user.phone ?? "");
    }
  }, [user]);

  // Redirect unauthenticated users
  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isHydrated, isAuthenticated, router]);

  async function handleSavePrivacy() {
    setSaving(true);
    setMessage(null);
    try {
      await updatePrivacy({ show_email: showEmail, show_phone: showPhone });
      setMessage("Configuración actualizada correctamente.");
    } catch (err) {
      const detail =
        err instanceof Error
          ? err.message
          : "No se pudo actualizar privacidad.";
      setMessage(`Error: ${detail}`);
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveProfile() {
    setProfileSaving(true);
    setMessage(null);
    try {
      await updateProfile({ 
        name: editName.trim() || undefined, 
        phone: editPhone.trim() || undefined 
      });
      setIsEditingProfile(false);
      setMessage("Perfil actualizado correctamente.");
    } catch (err) {
      const detail = err instanceof Error ? err.message : "Error al guardar el perfil.";
      setMessage(`Error: ${detail}`);
    } finally {
      setProfileSaving(false);
    }
  }

  async function handleSwitchRole() {
    if (isSwitching) return;
    setIsSwitching(true);
    try {
      // Toggle local view mode instantly
      toggleViewMode();
      // Optional: Delay for transition effect
      await new Promise(resolve => setTimeout(resolve, 600));
    } catch (err) {
      console.error("Error switching role:", err);
    } finally {
      setIsSwitching(false);
    }
  }

  function handleLogout() {
    logout();
    router.push("/");
  }

  const hasPrivacyChanges =
    showEmail !== (user?.show_email ?? false) ||
    showPhone !== (user?.show_phone ?? false);

  const isSeller = viewMode === "vendedor";

  useEffect(() => {
    if (!isSeller || !token) return;

    let active = true;

    async function fetchLocation() {
      setLocationLoading(true);
      setLocationMessage(null);

      try {
        const data = await api.get<SavedLocation | null>(
          "/locations/me",
          token || undefined,
        );
        if (!active) return;

        if (data) {
          setSelectedLocation({ lat: data.lat, lng: data.lng });
          setLocationCampus(data.campus || "UAO");
          setLocationLabel(data.label || "");
        } else {
          setSelectedLocation(null);
          setLocationCampus("UAO");
          setLocationLabel("");
        }
      } catch (err) {
        if (active) {
          const detail =
            err instanceof Error ? err.message : "No se pudo cargar ubicación.";
          setLocationMessage(`Error: ${detail}`);
        }
      } finally {
        if (active) {
          setLocationLoading(false);
        }
      }
    }

    fetchLocation();

    return () => {
      active = false;
    };
  }, [isSeller, token]);

  async function handleSaveLocation() {
    if (!token || !selectedLocation) {
      setLocationMessage("Selecciona un punto en el mapa antes de guardar.");
      return;
    }

    setLocationSaving(true);
    setLocationMessage(null);

    try {
      await api.put(
        "/locations/me",
        {
          lat: selectedLocation.lat,
          lng: selectedLocation.lng,
          campus: locationCampus || "UAO",
          label: locationLabel || null,
        },
        token || undefined,
      );
      setLocationMessage("Ubicación guardada correctamente.");
    } catch (err) {
      const detail =
        err instanceof Error ? err.message : "No se pudo guardar ubicación.";
      setLocationMessage(`Error: ${detail}`);
    } finally {
      setLocationSaving(false);
    }
  }

  async function handleDeleteLocation() {
    if (!token) return;

    setLocationSaving(true);
    setLocationMessage(null);

    try {
      await api.delete("/locations/me", token || undefined);
      setSelectedLocation(null);
      setLocationCampus("UAO");
      setLocationLabel("");
      setLocationMessage("Ubicación eliminada.");
    } catch (err) {
      const detail =
        err instanceof Error ? err.message : "No se pudo eliminar ubicación.";
      setLocationMessage(`Error: ${detail}`);
    } finally {
      setLocationSaving(false);
    }
  }

  if (!isHydrated || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Cargando perfil…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Mi Perfil</h1>
        <div className="flex gap-2">
          <Link href={`/users/${user.id}`}>
            <Button variant="outline" size="sm">
              👁️ Ver Perfil Público
            </Button>
          </Link>
          <Link href="/negotiations">
            <Button variant="secondary" size="sm">
              💬 Mis Negociaciones
            </Button>
          </Link>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Cerrar sesión
          </Button>
        </div>
      </div>

      {/* Loading Overlay for Switching */}
      {isSwitching && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white/40 backdrop-blur-md">
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-vera-100 rounded-full" />
              <div className="absolute top-0 w-16 h-16 border-4 border-vera-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-vera-800 font-bold tracking-tight animate-pulse">
              Reconfigurando interfaz...
            </p>
          </div>
        </div>
      )}

      {/* ── Cambio de Rol (HU 8.6) ── */}
      <section className="mb-6 rounded-2xl bg-gradient-to-br from-vera-600 to-vera-800 p-6 shadow-lg shadow-vera-600/20 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold">Modo de Interfaz (Rol)</h2>
            <p className="text-sm text-vera-100 mt-1">
              {isSeller 
                ? "Estás en modo VENDEDOR. Gestiona tus productos y ventas." 
                : "Estás en modo COMPRADOR. Explora el catálogo y compra."}
            </p>
          </div>
          <button
            onClick={handleSwitchRole}
            disabled={isSwitching}
            className="flex items-center gap-3 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 px-4 py-2 rounded-xl font-bold text-sm transition-all active:scale-95"
          >
            <svg 
              className={`h-5 w-5 transition-transform duration-500 ${isSeller ? "rotate-180" : "rotate-0"}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
            </svg>
            <span>{isSeller ? "Cambiar a Comprador" : "Cambiar a Vendedor"}</span>
          </button>
        </div>
      </section>

      {/* ── Información personal ── */}
      <section className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100 relative">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-700">
            Información Personal
          </h2>
          {!isEditingProfile ? (
            <Button variant="outline" size="sm" onClick={() => setIsEditingProfile(true)}>
              ✏️ Editar
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => {
                setIsEditingProfile(false);
                setEditName(user.name ?? "");
                setEditPhone(user.phone ?? "");
              }}>
                Cancelar
              </Button>
              <Button variant="primary" size="sm" onClick={handleSaveProfile} disabled={profileSaving}>
                {profileSaving ? "Guardando..." : "Guardar"}
              </Button>
            </div>
          )}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Input 
            label="Nombre" 
            value={isEditingProfile ? editName : (user.name || "—")} 
            onChange={(e) => setEditName(e.target.value)}
            disabled={!isEditingProfile} 
          />
          <Input label="Correo institucional" value={user.email} disabled />
          <Input
            label="Código institucional"
            value={user.institutional_id || "—"}
            disabled
          />
          <Input
            label="Teléfono"
            value={isEditingProfile ? editPhone : (user.phone || "No registrado")}
            onChange={(e) => setEditPhone(e.target.value)}
            placeholder="Ej: 3001234567"
            disabled={!isEditingProfile}
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
        <h2 className="mb-2 text-lg font-semibold text-gray-700">Privacidad</h2>
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
          <h2 className="text-lg font-semibold text-gray-700">
            Ubicación en Campus
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Haz clic en el mapa para fijar tu punto de entrega. Esta ubicación
            se usa para mostrar tus productos en el mapa de compradores.
          </p>

          {locationLoading ? (
            <p className="mt-4 text-sm text-gray-400">Cargando ubicación...</p>
          ) : (
            <>
              <div className="mt-4">
                <MapView
                  selectable
                  selectedLocation={selectedLocation}
                  onSelectLocation={(lat, lng) =>
                    setSelectedLocation({ lat, lng })
                  }
                  centerLat={selectedLocation?.lat ?? DEFAULT_LAT}
                  centerLng={selectedLocation?.lng ?? DEFAULT_LNG}
                  heightClassName="h-72"
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <Input
                  label="Campus"
                  value={locationCampus}
                  onChange={(e) => setLocationCampus(e.target.value)}
                  placeholder="UAO"
                />
                <Input
                  label="Referencia"
                  value={locationLabel}
                  onChange={(e) => setLocationLabel(e.target.value)}
                  placeholder="Ej: Cafetería central"
                />
              </div>

              <p className="mt-3 text-xs text-gray-500">
                {selectedLocation
                  ? `Coordenadas: ${selectedLocation.lat.toFixed(5)}, ${selectedLocation.lng.toFixed(5)}`
                  : "Selecciona un punto en el mapa para guardar tu ubicación."}
              </p>

              {locationMessage && (
                <p
                  className={`mt-2 text-sm ${
                    locationMessage.startsWith("Error:")
                      ? "text-red-600"
                      : "text-green-600"
                  }`}
                >
                  {locationMessage}
                </p>
              )}

              <div className="mt-4 flex flex-wrap gap-2">
                <Button
                  variant="primary"
                  size="md"
                  onClick={handleSaveLocation}
                  disabled={locationSaving || !selectedLocation}
                >
                  {locationSaving ? "Guardando..." : "Guardar ubicación"}
                </Button>
                <Button
                  variant="outline"
                  size="md"
                  onClick={handleDeleteLocation}
                  disabled={locationSaving}
                >
                  Quitar ubicación
                </Button>
              </div>
            </>
          )}
        </section>
      )}

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

      {isSeller && (
        <section className="mt-6 rounded-2xl bg-white p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-700">
              Gestión de Cupones
            </h2>
          </div>
          <CouponManager />
        </section>
      )}

      {/* Footer */}
      <footer className="mt-8 text-center text-xs text-gray-400">
        <p>Tus datos se gestionan conforme a la Ley 1581/2012.</p>
      </footer>
    </main>
  );
}
