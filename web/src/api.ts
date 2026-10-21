// Thin fetch wrapper: bearer token, transparent refresh and readable errors.

const TOKENS_KEY = "rsl.tokens";

export type Tokens = { access_token: string; refresh_token: string };

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export function loadTokens(): Tokens | null {
  try {
    const raw = localStorage.getItem(TOKENS_KEY);
    return raw ? (JSON.parse(raw) as Tokens) : null;
  } catch {
    return null;
  }
}

export function saveTokens(tokens: Tokens | null) {
  try {
    if (tokens) localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
    else localStorage.removeItem(TOKENS_KEY);
  } catch {
    /* storage unavailable: the session lives only in memory */
  }
  current = tokens;
}

let current: Tokens | null = loadTokens();
let onSessionLost: () => void = () => {};

export function setSessionLostHandler(handler: () => void) {
  onSessionLost = handler;
}

async function refresh(): Promise<boolean> {
  if (!current) return false;
  const response = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: current.refresh_token }),
  });
  if (!response.ok) return false;
  const data = await response.json();
  saveTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
  return true;
}

function errorMessage(body: unknown, status: number): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg);
  }
  return `Erro ${status}`;
}

export async function request<T = unknown>(
  path: string,
  options: RequestInit & { json?: unknown } = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (current) headers.set("Authorization", `Bearer ${current.access_token}`);
  let body = options.body;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  }
  const response = await fetch(`/api/v1${path}`, { ...options, headers, body });
  if (response.status === 401 && retry && current && !path.startsWith("/auth/")) {
    if (await refresh()) return request<T>(path, options, false);
    saveTokens(null);
    onSessionLost();
  }
  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json") ? await response.json() : await response.blob();
  if (!response.ok) throw new ApiError(response.status, errorMessage(data, response.status));
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, json?: unknown) => request<T>(path, { method: "POST", json }),
  patch: <T>(path: string, json?: unknown) => request<T>(path, { method: "PATCH", json }),
  put: <T>(path: string, json?: unknown) => request<T>(path, { method: "PUT", json }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  upload: <T>(path: string, form: FormData) => request<T>(path, { method: "POST", body: form }),
};
