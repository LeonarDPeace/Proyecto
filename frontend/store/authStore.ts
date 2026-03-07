/**
 * Zustand Store — Autenticación global.
 *
 * Gestiona el estado del usuario autenticado y el token JWT.
 * Sprint 0: Estructura base. Sprint 1: Persistencia + refresh token.
 */

import { create } from "zustand";

interface User {
  id: string;
  name: string;
  email: string;
  role: "vendedor" | "comprador";
  is_verified: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,

  login: (token: string, user: User) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("veramarket_token", token);
    }
    set({ token, user });
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("veramarket_token");
    }
    set({ user: null, token: null });
  },

  setUser: (user: User) => set({ user }),
}));
