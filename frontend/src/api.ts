import type { AdminStats, Booking, Property, Role, User } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = sessionStorage.getItem("stayease_token");
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new ApiClientError(payload.error || "The request failed", response.status);
  }
  return payload as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (payload: {
    fullName: string;
    email: string;
    password: string;
    phone?: string;
    role: Exclude<Role, "ADMIN">;
  }) =>
    request<{ token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  me: () => request<{ user: User }>("/auth/me"),
  properties: (params = new URLSearchParams()) =>
    request<{ items: Property[]; total: number }>(`/properties?${params}`),
  property: (id: number) => request<{ property: Property }>(`/properties/${id}`),
  createProperty: (payload: Record<string, unknown>) =>
    request<{ property: Property }>("/properties", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  addAvailability: (
    propertyId: number,
    payload: { startDate: string; endDate: string; pricePerNight: number; note?: string },
  ) =>
    request(`/properties/${propertyId}/availability`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  createBooking: (payload: {
    propertyId: number;
    checkIn: string;
    checkOut: string;
    guestCount: number;
  }) =>
    request<{ booking: Booking }>("/bookings", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  bookings: () => request<{ items: Booking[] }>("/bookings"),
  pay: (bookingId: number) => {
    const storageKey = `stayease_payment_key_${bookingId}`;
    const idempotencyKey = sessionStorage.getItem(storageKey) || crypto.randomUUID();
    sessionStorage.setItem(storageKey, idempotencyKey);
    return request<{ booking: Booking }>(`/bookings/${bookingId}/pay`, {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: "{}",
    }).then((result) => {
      sessionStorage.removeItem(storageKey);
      return result;
    });
  },
  cancel: (bookingId: number, reason: string) =>
    request<{ booking: Booking }>(`/bookings/${bookingId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  stats: () => request<AdminStats>("/admin/stats"),
};
