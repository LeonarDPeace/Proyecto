"use client"; // Fixed motion import

/**
 * NavigationMenu — Menú de navegación global (Sprint 3).
 *
 * Renderiza una barra de navegación superior en desktop y una barra inferior
 * (bottom-tab) en móvil, siguiendo el patrón PWA estándar.
 *
 * Rutas principales:
 *   - Inicio  (/)
 *   - Catálogo (/products)
 *   - Mapa    (/map)
 *   - Perfil  (/profile)  — si autenticado
 *   - Login   (/auth)     — si no autenticado
 */

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";

import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

console.log("Motion defined:", !!motion);

/* ------------------------------------------------------------------ */
/*  Iconos SVG inline (evita dependencia de librería externa)          */
/* ------------------------------------------------------------------ */

function HomeIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
      />
    </svg>
  );
}

function CatalogIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.15c0 .414.336.75.75.75z"
      />
    </svg>
  );
}

function MapIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
      />
    </svg>
  );
}

function ProfileIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
      />
    </svg>
  );
}

function LoginIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9"
      />
    </svg>
  );
}

function PlusIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 2}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 4.5v15m7.5-7.5h-15"
      />
    </svg>
  );
}

function ChatIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"
      />
    </svg>
  );
}

function ChartPieIcon({ active }: { active: boolean }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={active ? 0 : 1.75}
      className="h-6 w-6"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10.5 6a7.5 7.5 0 107.5 7.5h-7.5V6z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13.5 10.5H21A7.5 7.5 0 0013.5 3v7.5z"
      />
    </svg>
  );
}

function SwitchIcon({ isSeller }: { isSeller: boolean }) {
  return (
    <motion.svg
      animate={{ rotate: isSeller ? 180 : 0 }}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      className="h-5 w-5"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"
      />
    </motion.svg>
  );
}


/* ------------------------------------------------------------------ */
/*  Tipos                                                              */
/* ------------------------------------------------------------------ */

interface NavItem {
  label: string;
  href: string;
  icon: (props: { active: boolean }) => React.ReactNode;
  /** Mostrar solo cuando hay autenticación */
  authOnly?: boolean;
  /** Mostrar solo cuando NO hay autenticación */
  guestOnly?: boolean;
  /** Mostrar solo para vendedores */
  sellerOnly?: boolean;
  /** Mostrar solo para administradores */
  adminOnly?: boolean;
}

/* ------------------------------------------------------------------ */
/*  Componente principal                                               */
/* ------------------------------------------------------------------ */

export default function NavigationMenu() {
  const pathname = usePathname();
  const { isAuthenticated, isHydrated, user, switchRole, viewMode, toggleViewMode } = useAuth();
  const [isSwitching, setIsSwitching] = useState(false);

  const isSeller = viewMode === "vendedor";
  const isAdmin = user?.role === "admin";
  const canSwitch = isAuthenticated; // Habilitado para todos en desarrollo para verificación

  const handleSwitchRole = async () => {
    if (isSwitching) return;
    setIsSwitching(true);
    try {
      await switchRole();
      // Optional: Small delay to show off the premium transition
      await new Promise(resolve => setTimeout(resolve, 600));
    } catch (err) {
      console.error("Error switching role:", err);
    } finally {
      setIsSwitching(false);
    }
  };

  const navItems: NavItem[] = [
    { label: "Inicio", href: "/", icon: HomeIcon },
    { label: "Catálogo", href: "/products", icon: CatalogIcon },
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: ChartPieIcon,
      authOnly: true,
      sellerOnly: true,
    },
    {
      label: "Admin",
      href: "/admin",
      icon: ChartPieIcon,
      authOnly: true,
      adminOnly: true,
    },
    {
      label: "Publicar",
      href: "/products/new",
      icon: PlusIcon,
      authOnly: true,
      sellerOnly: true,
    },


    {
      label: "Negociaciones",
      href: "/negotiations",
      icon: ChatIcon,
      authOnly: true,
    },
    { label: "Mapa", href: "/map", icon: MapIcon },
    { label: "Perfil", href: "/profile", icon: ProfileIcon, authOnly: true },
    { label: "Entrar", href: "/auth", icon: LoginIcon, guestOnly: true },
  ];

  // Filtrar items según estado de autenticación
  const visibleItems = navItems.filter((item) => {
    if (!isHydrated) {
      // Antes de hidratar, mostrar solo los públicos
      return !item.authOnly && !item.guestOnly;
    }
    if (item.authOnly && !isAuthenticated) return false;
    if (item.guestOnly && isAuthenticated) return false;
    if (item.sellerOnly && !isSeller) return false;
    if (item.adminOnly && !isAdmin) return false;
    return true;

  });

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Loading Overlay for Switching */}
      {isSwitching && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-white/40 backdrop-blur-md"
        >
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-vera-100 rounded-full" />
              <div className="absolute top-0 w-16 h-16 border-4 border-vera-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-vera-800 font-bold tracking-tight animate-pulse">
              Reconfigurando interfaz...
            </p>
          </div>
        </motion.div>
      )}

      {/* ── Desktop: Barra superior ────────────────────────────── */}
      <nav
        id="nav-desktop"
        className="hidden md:flex fixed top-0 left-0 right-0 z-50 items-center justify-between border-b border-vera-100 bg-white/80 backdrop-blur-lg px-6 py-3 shadow-sm"
      >
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-vera-600 rounded-xl flex items-center justify-center text-white font-black text-sm shadow-lg shadow-vera-600/20 group-hover:scale-110 transition-transform">
            V
          </div>
          <span className="text-xl font-bold tracking-tight text-vera-700">
            Vera
            <span className="text-vera-500">Market</span>
          </span>
        </Link>

        {/* Links centrales - Scrollable horizontally */}
        <div className="flex items-center gap-1 bg-gray-100/50 p-1 rounded-xl overflow-x-auto no-scrollbar max-w-[60%]">
          {visibleItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-300
                  ${
                    active
                      ? "bg-white text-vera-700 shadow-sm"
                      : "text-gray-500 hover:text-vera-600"
                  }
                `}
              >
                <item.icon active={active} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Spacer derecho / Switch Role (HU 5.x) */}
        <div className="flex items-center gap-4 w-auto min-w-[160px] justify-end">
          {isHydrated && isAuthenticated && canSwitch && (
            <button
              onClick={handleSwitchRole}
              disabled={isSwitching}
              className={`
                group relative flex items-center gap-3 rounded-2xl px-4 py-2 text-xs font-black tracking-tighter uppercase transition-all duration-500
                ${
                  isSeller
                    ? "bg-vera-600 text-white shadow-lg shadow-vera-600/30"
                    : "bg-white text-gray-700 border border-gray-200 shadow-sm hover:border-vera-300"
                }
                ${isSwitching ? "opacity-50 cursor-wait" : "hover:scale-105 active:scale-95"}
              `}
              title={isSeller ? "Cambiar a Comprador" : "Cambiar a Vendedor"}
            >
              <SwitchIcon isSeller={isSeller} />
              <span>{isSeller ? "Vendedor" : "Comprador"}</span>
              <div className={`
                absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white
                ${isSeller ? "bg-emerald-400" : "bg-blue-400"}
              `} />
            </button>
          )}
        </div>
      </nav>

      {/* ── Mobile: Barra inferior (bottom-tab) ────────────────── */}
      <nav
        id="nav-mobile"
        className="md:hidden fixed bottom-0 left-0 right-0 z-50 flex items-center justify-start overflow-x-auto no-scrollbar border-t border-vera-100 bg-white/90 backdrop-blur-xl pb-[env(safe-area-inset-bottom)] shadow-[0_-10px_40px_rgba(0,0,0,0.08)]"
      >
        {visibleItems.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                relative flex flex-col items-center gap-1 py-3 px-3 text-[10px] font-bold uppercase tracking-widest transition-all duration-300
                ${active ? "text-vera-600" : "text-gray-400"}
              `}
            >
              {active && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute top-0 w-8 h-1 bg-vera-600 rounded-full"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <item.icon active={active} />
              <span>{item.label}</span>
            </Link>
          );
        })}

        {/* Mobile Switch Role Button (HU 5.x) */}
        {isHydrated && isAuthenticated && canSwitch && (
          <button
            onClick={handleSwitchRole}
            disabled={isSwitching}
            className={`
              flex flex-col items-center gap-1 py-3 px-3 text-[10px] font-black uppercase tracking-widest transition-all
              ${isSeller ? "text-vera-600" : "text-gray-400"}
              ${isSwitching ? "opacity-50" : ""}
            `}
          >
            <div className={`
              relative p-1 rounded-xl transition-all
              ${isSeller ? "bg-vera-50" : "bg-gray-100"}
            `}>
               <SwitchIcon isSeller={isSeller} />
               {isSwitching && (
                 <div className="absolute inset-0 border-2 border-vera-500 border-t-transparent rounded-xl animate-spin" />
               )}
            </div>
            <span>{isSeller ? "Tienda" : "Compra"}</span>
          </button>
        )}
      </nav>
    </>
  );
}
