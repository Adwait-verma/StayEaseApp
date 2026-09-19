import {
  ArrowLeft,
  BedDouble,
  CalendarDays,
  Check,
  MapPin,
  ShieldCheck,
  Star,
  UsersRound,
} from "lucide-react";
import { type FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ApiClientError, api } from "../api";
import { useAuth } from "../auth";
import { demoProperties } from "../demo";
import type { Property } from "../types";


const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const futureDate = (offset: number) => {
  const value = new Date();
  value.setDate(value.getDate() + offset);
  return value.toISOString().slice(0, 10);
};

export function PropertyPage() {
  const { id } = useParams();
  const propertyId = Number(id);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [property, setProperty] = useState<Property | null>(null);
  const [preview, setPreview] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [booking, setBooking] = useState(false);
  const [checkIn, setCheckIn] = useState(futureDate(14));
  const [checkOut, setCheckOut] = useState(futureDate(17));
  const [guestCount, setGuestCount] = useState(2);

  useEffect(() => {
    api
      .property(propertyId)
      .then(({ property: response }) => setProperty(response))
      .catch(() => {
        setProperty(demoProperties.find((item) => item.id === propertyId) || null);
        setPreview(true);
      })
      .finally(() => setLoading(false));
  }, [propertyId]);

  const nights = useMemo(() => {
    const start = new Date(checkIn).getTime();
    const end = new Date(checkOut).getTime();
    return Math.max(0, Math.round((end - start) / 86_400_000));
  }, [checkIn, checkOut]);

  const reserve = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) {
      navigate("/login", { state: { from: `/properties/${propertyId}` } });
      return;
    }
    setBooking(true);
    setError("");
    try {
      await api.createBooking({ propertyId, checkIn, checkOut, guestCount });
      navigate("/dashboard");
    } catch (caught) {
      setError(caught instanceof ApiClientError ? caught.message : "Could not create booking");
    } finally {
      setBooking(false);
    }
  };

  if (loading) return <main className="shell page-loader">Opening this stay…</main>;
  if (!property) {
    return (
      <main className="shell section empty-state">
        This property could not be found. <Link to="/">Return to explore</Link>
      </main>
    );
  }

  return (
    <main className="property-page shell section">
      <Link className="back-link" to="/">
        <ArrowLeft size={17} /> Back to stays
      </Link>
      {preview && <div className="preview-banner">Preview listing · connect the API to book</div>}
      <div className="detail-hero">
        <img src={property.coverImage || "/images/goa-villa.svg"} alt={property.title} />
        <div className="detail-title-card">
          <div className="eyebrow">Hosted by {property.hostName}</div>
          <h1>{property.title}</h1>
          <div className="detail-location">
            <MapPin size={17} /> {property.city}, {property.country}
          </div>
          <div className="rating-line">
            <Star size={17} fill="currentColor" /> {property.averageRating.toFixed(1)} ·{" "}
            {property.reviewCount} verified reviews
          </div>
        </div>
      </div>
      <div className="detail-layout">
        <section className="detail-content">
          <div className="quick-facts">
            <span>
              <UsersRound /> Up to {property.capacity} guests
            </span>
            <span>
              <BedDouble /> {property.bedrooms} bedrooms
            </span>
            <span>
              <ShieldCheck /> Verified host
            </span>
          </div>
          <div className="detail-block">
            <h2>About this stay</h2>
            <p>{property.description}</p>
          </div>
          <div className="detail-block">
            <h2>What this place offers</h2>
            <div className="amenity-grid">
              {property.amenities.map((amenity) => (
                <span key={amenity}>
                  <Check size={17} /> {amenity}
                </span>
              ))}
            </div>
          </div>
          <div className="integrity-note">
            <ShieldCheck size={24} />
            <div>
              <strong>Booking protection built in</strong>
              <p>
                StayEase locks this property while your dates are validated, preventing two guests
                from reserving an overlapping stay.
              </p>
            </div>
          </div>
        </section>
        <aside className="booking-card">
          <div className="booking-price">
            <strong>{money.format(property.basePrice)}</strong>
            <span>/ night</span>
          </div>
          <form onSubmit={reserve}>
            <div className="date-pair">
              <label>
                Check in
                <input
                  type="date"
                  min={futureDate(1)}
                  value={checkIn}
                  onChange={(event) => setCheckIn(event.target.value)}
                  required
                />
              </label>
              <label>
                Check out
                <input
                  type="date"
                  min={checkIn}
                  value={checkOut}
                  onChange={(event) => setCheckOut(event.target.value)}
                  required
                />
              </label>
            </div>
            <label>
              Guests
              <div className="field-with-icon bordered-field">
                <UsersRound size={17} />
                <input
                  type="number"
                  min="1"
                  max={property.capacity}
                  value={guestCount}
                  onChange={(event) => setGuestCount(Number(event.target.value))}
                />
              </div>
            </label>
            {error && <div className="form-error">{error}</div>}
            <button className="button button-wide" disabled={booking || nights < 1}>
              {booking ? "Checking availability…" : user ? "Reserve this stay" : "Sign in to reserve"}
            </button>
          </form>
          <p className="booking-hint">You won’t be charged. Payments are simulated for this demo.</p>
          <div className="price-breakdown">
            <span>
              {money.format(property.basePrice)} × {nights} nights
            </span>
            <strong>{money.format(property.basePrice * nights)}</strong>
          </div>
          <div className="booking-secure">
            <CalendarDays size={16} /> Dates verified before confirmation
          </div>
        </aside>
      </div>
    </main>
  );
}
