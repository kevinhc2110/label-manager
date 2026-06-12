import { Printer, PrintLabelResponse } from "../types/printer";

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.2.2:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export function getPrinters(): Promise<Printer[]> {
  return request("/printers");
}

export function printLabel(printerId: string): Promise<PrintLabelResponse> {
  return request(`/printers/${printerId}/print`, { method: "POST" });
}
