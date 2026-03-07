"use client";

/**
 * Hook — useAuth: gestión del estado de autenticación.
 *
 * Sprint 0: Estructura base. Sprint 1: Conectar con API + JWT.
 */

import { useAuthStore } from "@/store/authStore";

export function useAuth() {
  const { user, token, login, logout } = useAuthStore();

  const isAuthenticated = !!token;

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
  };
}
