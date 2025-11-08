import type { Product, QrCode, User } from "./types";

export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const authHeaders = () => {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    const message = detail.detail ?? response.statusText;
    throw new Error(typeof message === "string" ? message : "Request failed");
  }
  return response.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<{ access_token: string; refresh_token: string }>(response);
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    headers: authHeaders(),
  });
  return handleResponse<User>(response);
}

export async function fetchQRCodes(params: { status?: string; product_id?: number } = {}): Promise<QrCode[]> {
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.product_id) query.set("product_id", params.product_id.toString());
  const queryString = query.toString();
  const url = queryString ? `${API_BASE}/api/qrcodes/?${queryString}` : `${API_BASE}/api/qrcodes/`;
  const response = await fetch(url, {
    headers: authHeaders(),
  });
  return handleResponse<QrCode[]>(response);
}

export async function createQRCode(form: FormData): Promise<QrCode> {
  const response = await fetch(`${API_BASE}/api/qrcodes/generate`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  return handleResponse<QrCode>(response);
}

export async function fetchProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/api/products/`, {
    headers: authHeaders(),
  });
  return handleResponse<Product[]>(response);
}

export async function revokeQRCode(id: number): Promise<QrCode> {
  const response = await fetch(`${API_BASE}/api/qrcodes/${id}/revoke`, {
    method: "POST",
    headers: authHeaders(),
  });
  return handleResponse<QrCode>(response);
}
