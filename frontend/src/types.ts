export type Role = "ADMIN" | "HOST" | "GUEST";

export interface User {
  id: number;
  fullName: string;
  email: string;
  phone?: string | null;
  roles: Role[];
  active: boolean;
}

export interface AvailabilityWindow {
  id: number;
  startDate: string;
  endDate: string;
  pricePerNight: number;
  note?: string | null;
}

export interface Property {
  id: number;
  hostId: number;
  hostName: string;
  title: string;
  slug: string;
  description: string;
  addressLine?: string;
  city: string;
  country: string;
  capacity: number;
  bedrooms: number;
  bathrooms: number;
  basePrice: number;
  averageRating: number;
  reviewCount: number;
  active: boolean;
  coverImage?: string | null;
  amenities: string[];
  images?: Array<{ url: string; alt: string; order: number }>;
  availability?: AvailabilityWindow[];
}

export interface Booking {
  id: number;
  guestId: number;
  property: {
    id: number;
    title: string;
    city: string;
    coverImage?: string | null;
  };
  checkIn: string;
  checkOut: string;
  guestCount: number;
  nightlyRate: number;
  totalNights: number;
  totalAmount: number;
  status: "PENDING" | "CONFIRMED" | "CANCELLED" | "COMPLETED";
  cancellationReason?: string | null;
  payment?: {
    status: string;
    reference?: string | null;
    paidAt?: string | null;
  } | null;
  review?: {
    id: number;
    rating: number;
    comment?: string | null;
  } | null;
  createdAt: string;
}

export interface AdminStats {
  users: number;
  activeProperties: number;
  bookings: number;
  paidRevenue: number;
  bookingsByStatus: Record<string, number>;
}
