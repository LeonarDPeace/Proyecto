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
  login: (token: string, user: User, isNewUser?: boolean) => void;
  logout: () => void;
  setUser: (user: User) => void;
  setIsNewUser: (value: boolean) => void;
  hydrate: () => void;
}

const TOKEN_KEY = "veramarket_token";
const USER_KEY = "veramarket_user";

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isNewUser: false,
  isHydrated: false,

  login: (token: string, user: User, isNewUser = false) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    set({ token, user, isNewUser });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    set({ user: null, token: null, isNewUser: false });
  },

  setUser: (user: User) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    set({ user });
  },

  setIsNewUser: (value: boolean) => set({ isNewUser: value }),

  hydrate: () => {
    if (typeof window === "undefined") return;
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    let user: User | null = null;
    if (userStr) {
      try {
        user = JSON.parse(userStr);
      } catch {
        localStorage.removeItem(USER_KEY);
      }
    }
    set({ token, user, isHydrated: true });
  },
}));
