/**
 * Zustand Store — Autenticación global (Sprint 1).
 *
 * Gestiona el estado del usuario autenticado y el token JWT.
 * Soporta flujo OTP: request → verify → complete profile.
 * Persiste token en localStorage con rehidratación al cargar la página.
 */

import { create } from "zustand";

export interface User {
  id: string;
  name: string;
  email: string;
  role: "vendedor" | "comprador";
  vendor_status?: "pending" | "approved" | "rejected";
  is_verified: boolean;

  institutional_id?: string;
  phone?: string | null;
  show_email?: boolean;
  show_phone?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isNewUser: boolean;
  isHydrated: boolean;
  viewMode: "vendedor" | "comprador" | null;
  login: (token: string, user: User, isNewUser?: boolean) => void;
  logout: () => void;
  setUser: (user: User) => void;
  setIsNewUser: (value: boolean) => void;
  toggleViewMode: () => void;
  hydrate: () => void;
}

const TOKEN_KEY = "veramarket_token";
const USER_KEY = "veramarket_user";
const VIEW_MODE_KEY = "veramarket_view_mode";

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isNewUser: false,
  isHydrated: false,
  viewMode: null,

  login: (token: string, user: User, isNewUser = false) => {
    const viewMode = user.role;
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
      localStorage.setItem(VIEW_MODE_KEY, viewMode);
    }
    set({ token, user, isNewUser, viewMode });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      localStorage.removeItem(VIEW_MODE_KEY);
    }
    set({ user: null, token: null, isNewUser: false, viewMode: null });
  },

  setUser: (user: User) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    set({ user });
  },

  toggleViewMode: () => {
    const current = get().viewMode;
    const next = current === "vendedor" ? "comprador" : "vendedor";
    if (typeof window !== "undefined") {
      localStorage.setItem(VIEW_MODE_KEY, next);
    }
    set({ viewMode: next });
  },

  setIsNewUser: (value: boolean) => set({ isNewUser: value }),

  hydrate: () => {
    if (typeof window === "undefined") return;
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    const viewMode = localStorage.getItem(VIEW_MODE_KEY) as any;

    let user: User | null = null;
    if (userStr) {
      try {
        user = JSON.parse(userStr);
      } catch {
        localStorage.removeItem(USER_KEY);
      }
    }
    set({ token, user, viewMode: viewMode || user?.role || null, isHydrated: true });
  },
}));
