/**
 * Utilidades de autenticación — gestión de tokens JWT en el cliente.
 *
 * Sprint 0: Estructura base. Sprint 1: Implementación completa.
 */

const TOKEN_KEY = "veramarket_token";
const REFRESH_KEY = "veramarket_refresh";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
