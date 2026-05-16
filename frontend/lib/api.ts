/**
 * Cliente HTTP — wrapper sobre fetch para comunicarse con la API de VeraMarket.
 *
 * Incluye manejo automático de JWT y base URL desde variables de entorno.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const TOKEN_KEY = "veramarket_token";
const USER_KEY = "veramarket_user";

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  token?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const { body, token, headers: customHeaders, ...restOptions } = options;

    const headers: Record<string, string> = {
      ...((customHeaders as Record<string, string>) || {}),
    };

    if (body !== undefined && body !== null) {
      headers["Content-Type"] = "application/json";
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...restOptions,
        headers,
        body:
          body !== undefined && body !== null
            ? JSON.stringify(body)
            : undefined,
      });
    } catch {
      throw new Error(
        `No se pudo conectar con la API (${this.baseUrl}${endpoint}). Verifica backend, URL y CORS.`,
      );
    }

    if (response.status === 401 && token && typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      window.dispatchEvent(new Event("veramarket:unauthorized"));
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(
        error.detail || `Error HTTP ${response.status}: ${response.statusText}`,
      );
    }

    return response.json();
  }

  async get<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET", token });
  }

  async post<T>(endpoint: string, body: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: "POST", body, token });
  }

  async put<T>(endpoint: string, body: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: "PUT", body, token });
  }

  async delete<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE", token });
  }

  async patch<T>(endpoint: string, body?: unknown, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: "PATCH", body, token });
  }
}

export const api = new ApiClient(API_BASE_URL);
export default api;
