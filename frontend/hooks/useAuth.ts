"use client";

/**
 * Hook — useAuth: gestión del estado de autenticación (Sprint 1).
 *
 * Soporta flujo OTP: request → verify → complete profile.
 * Rehidrata token de localStorage al montar.
 */

import { useEffect } from "react";

import { useAuthStore } from "@/store/authStore";
import api from "@/lib/api";

export function useAuth() {
  const {
    user,
    token,
    isNewUser,
    isHydrated,
    login,
    logout,
    setUser,
    setIsNewUser,
    hydrate,
  } = useAuthStore();

  // Rehidratar desde localStorage al montar
  useEffect(() => {
    if (!isHydrated) {
      hydrate();
    }
  }, [isHydrated, hydrate]);

  // Validar token rehidratado para evitar estados inconsistentes en UI.
  useEffect(() => {
    if (!isHydrated || !token) return;

    let active = true;

    const validateSession = async () => {
      try {
        const profile = await api.get<{
          id: string;
          name: string;
          email: string;
          role: "vendedor" | "comprador";
          is_verified: boolean;
          institutional_id: string;
          phone: string | null;
          show_email: boolean;
          show_phone: boolean;
        }>("/users/me", token);

        if (active) {
          setUser(profile);
        }
      } catch {
        if (active) {
          logout();
        }
      }
    };

    validateSession();

    return () => {
      active = false;
    };
  }, [isHydrated, token, logout, setUser]);

  // Si el backend responde 401 para una petición autenticada, sincronizar estado.
  useEffect(() => {
    if (typeof window === "undefined") return;

    const onUnauthorized = () => {
      logout();
    };

    window.addEventListener("veramarket:unauthorized", onUnauthorized);
    return () => {
      window.removeEventListener("veramarket:unauthorized", onUnauthorized);
    };
  }, [logout]);

  const isAuthenticated = !!token;

  /** Solicita un código OTP al correo institucional */
  async function requestOTP(email: string) {
    return api.post<{ message: string; email: string; expires_in_minutes: number }>(
      "/auth/otp/request",
      { email }
    );
  }

  /** Verifica el código OTP y obtiene token JWT */
  async function verifyOTP(email: string, code: string) {
    const response = await api.post<{
      access_token: string;
      token_type: string;
      is_new_user: boolean;
    }>("/auth/otp/verify", { email, code });

    // Fetch user profile with the new token
    const userProfile = await api.get<{
      id: string;
      name: string;
      email: string;
      role: "vendedor" | "comprador";
      is_verified: boolean;
      institutional_id: string;
      phone: string | null;
      show_email: boolean;
      show_phone: boolean;
    }>("/users/me", response.access_token);

    login(response.access_token, userProfile, response.is_new_user);
    return response;
  }

  /** Completa el perfil de un usuario nuevo */
  async function completeProfile(data: {
    name: string;
    institutional_id: string;
    phone?: string;
    accept_terms: boolean;
  }) {
    const updatedUser = await api.post<{
      id: string;
      name: string;
      email: string;
      role: "vendedor" | "comprador";
      is_verified: boolean;
      institutional_id: string;
      phone: string | null;
      show_email: boolean;
      show_phone: boolean;
    }>("/auth/profile/complete", data, token || undefined);

    setUser(updatedUser);
    setIsNewUser(false);
    return updatedUser;
  }

  /** Actualiza la configuración de privacidad */
  async function updatePrivacy(settings: {
    show_email: boolean;
    show_phone: boolean;
  }) {
    const result = await api.put<{ show_email: boolean; show_phone: boolean }>(
      "/users/me/privacy",
      settings,
      token || undefined
    );
    if (user) {
      setUser({ ...user, ...result });
    }
    return result;
  }

  return {
    user,
    token,
    isAuthenticated,
    isNewUser,
    isHydrated,
    login,
    logout,
    requestOTP,
    verifyOTP,
    completeProfile,
    updatePrivacy,
  };
}
