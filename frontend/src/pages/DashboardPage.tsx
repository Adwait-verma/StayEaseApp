import { CalendarDays, CheckCircle2, Clock3, CreditCard, MapPin, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiClientError, api } from "../api";
import { useAuth } from "../auth";
import type { Booking } from "../types";


const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const statusIcon = {
  PENDING: Clock3,
  CONFIRMED: CheckCircle2,
  CANCELLED: XCircle,
  COMPLETED: CheckCircle2,
};

export function DashboardPage() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    api
      .bookings()
      .then(({ items }) => setBookings(items))
      .catch((caught) =>
        setError(caught instanceof ApiClientError ? caught.message : "Could not load bookings"),
      )
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const pay = async (id: number) => {
    setBusyId(id);
    setError("");
    try {
      await api.pay(id);
      load();
    } catch (caught) {
      setError(caught instanceof ApiClientError ? caught.message : "Payment failed");
      setBusyId(null);
    }
  };

  const cancel = async (id: number) => {
    const reason = window.prompt("Why are you cancelling this booking?");
    if (!reason) return;
    setBusyId(id);
    try {
      await api.cancel(id, reason);
      load();
    } catch (caught) {
      setError(caught instanceof ApiClientError ? caught.message : "Cancellation failed");
      setBusyId(null);
    }
  };

  return (
    <main className="shell section dashboard-page">
      <div className="dashboard-heading">
        <div>
          <div className="eyebrow">Guest dashboard</div>
          <h1>Welcome back, {user?.fullName.split(" ")[0]}</h1>
          <p>Every booking, payment, and stay status in one place.</p>
        </div>
        <Link className="button" to="/">
          Explore more stays
        </Link>
      </div>
      <div className="dashboard-summary">
        <article>
          <span>Upcoming</span>
          <strong>{bookings.filter((item) => item.status === "CONFIRMED").length}</strong>
        </article>
        <article>
          <span>Awaiting payment</span>
          <strong>{bookings.filter((item) => item.status === "PENDING").length}</strong>
        </article>
        <article>
          <span>Completed stays</span>
          <strong>{bookings.filter((item) => item.status === "COMPLETED").length}</strong>
        </article>
      </div>
      {error && <div className="form-error">{error}</div>}
      {loading ? (
        <div className="page-loader">Loading your trips…</div>
      ) : bookings.length ? (
        <div className="booking-list">
          {bookings.map((booking) => {
            const Icon = statusIcon[booking.status];
            return (
              <article className="trip-card" key={booking.id}>
                <img
                  src={booking.property.coverImage || "/images/goa-villa.svg"}
                  alt={booking.property.title}
                />
                <div className="trip-content">
                  <div className={`status status-${booking.status.toLowerCase()}`}>
                    <Icon size={15} /> {booking.status.toLowerCase()}
                  </div>
                  <h2>{booking.property.title}</h2>
                  <p>
                    <MapPin size={16} /> {booking.property.city}
                  </p>
                  <div className="trip-details">
                    <span>
                      <CalendarDays size={16} /> {booking.checkIn} → {booking.checkOut}
                    </span>
                    <span>{booking.guestCount} guests</span>
                    <strong>{money.format(booking.totalAmount)}</strong>
                  </div>
                  <div className="trip-actions">
                    {booking.status === "PENDING" && (
                      <button
                        className="button button-small"
                        disabled={busyId === booking.id}
                        onClick={() => pay(booking.id)}
                      >
                        <CreditCard size={16} /> Complete demo payment
                      </button>
                    )}
                    {(["PENDING", "CONFIRMED"] as string[]).includes(booking.status) && (
                      <button
                        className="button-secondary button-small"
                        disabled={busyId === booking.id}
                        onClick={() => cancel(booking.id)}
                      >
                        Cancel booking
                      </button>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <CalendarDays size={32} />
          <h2>No trips yet</h2>
          <p>When you reserve a stay, its status and payment will appear here.</p>
        </div>
      )}
    </main>
  );
}
