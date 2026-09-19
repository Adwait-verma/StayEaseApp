import {
  ArrowRight,
  CalendarCheck2,
  DatabaseZap,
  MapPin,
  Search,
  ShieldCheck,
  Sparkles,
  UsersRound,
} from "lucide-react";
import { type FormEvent, useCallback, useEffect, useState } from "react";

import { api } from "../api";
import { PropertyCard } from "../components/PropertyCard";
import { demoProperties } from "../demo";
import type { Property } from "../types";


export function HomePage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [preview, setPreview] = useState(false);
  const [loading, setLoading] = useState(true);
  const [city, setCity] = useState("");
  const [checkIn, setCheckIn] = useState("");
  const [checkOut, setCheckOut] = useState("");
  const [guests, setGuests] = useState("2");

  const loadProperties = useCallback((params = new URLSearchParams(), fallbackCity = "") => {
    setLoading(true);
    api
      .properties(params)
      .then(({ items }) => {
        setProperties(items);
        setPreview(false);
      })
      .catch(() => {
        const filtered = fallbackCity
          ? demoProperties.filter((property) =>
              property.city.toLowerCase().includes(fallbackCity.toLowerCase()),
            )
          : demoProperties;
        setProperties(filtered);
        setPreview(true);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => loadProperties(), [loadProperties]);

  const search = (event: FormEvent) => {
    event.preventDefault();
    const params = new URLSearchParams();
    if (city) params.set("city", city);
    if (checkIn) params.set("checkIn", checkIn);
    if (checkOut) params.set("checkOut", checkOut);
    if (guests) params.set("guests", guests);
    loadProperties(params, city);
  };

  return (
    <main>
      <section className="hero">
        <div className="hero-orb hero-orb-one" />
        <div className="hero-orb hero-orb-two" />
        <div className="shell hero-grid">
          <div className="hero-copy">
            <div className="eyebrow">
              <Sparkles size={16} /> Thoughtful stays across India
            </div>
            <h1>
              Find your place.
              <span>Stay without the stress.</span>
            </h1>
            <p>
              Discover character-filled homes with clear pricing, verified stays, and booking
              protection designed into the database—not added as an afterthought.
            </p>
            <div className="hero-proof">
              <span>
                <ShieldCheck size={18} /> Conflict-safe bookings
              </span>
              <span>
                <CalendarCheck2 size={18} /> Live availability
              </span>
            </div>
          </div>
          <div className="hero-visual" aria-label="Featured StayEase property collage">
            <img src="/images/goa-villa.svg" alt="Sunset Courtyard Villa" />
            <div className="floating-review">
              <div className="avatar-stack">MK</div>
              <div>
                <strong>“It felt effortless.”</strong>
                <span>Verified guest · Goa</span>
              </div>
            </div>
            <div className="floating-stat">
              <strong>4.9</strong>
              <span>guest rating</span>
            </div>
          </div>
        </div>
        <form className="shell search-panel" onSubmit={search}>
          <label>
            <span>Where</span>
            <div className="field-with-icon">
              <MapPin size={18} />
              <input
                value={city}
                onChange={(event) => setCity(event.target.value)}
                placeholder="Goa, Manali, Jaipur…"
              />
            </div>
          </label>
          <label>
            <span>Check in</span>
            <input type="date" value={checkIn} onChange={(event) => setCheckIn(event.target.value)} />
          </label>
          <label>
            <span>Check out</span>
            <input
              type="date"
              value={checkOut}
              onChange={(event) => setCheckOut(event.target.value)}
            />
          </label>
          <label>
            <span>Guests</span>
            <div className="field-with-icon">
              <UsersRound size={18} />
              <input
                type="number"
                min="1"
                max="50"
                value={guests}
                onChange={(event) => setGuests(event.target.value)}
              />
            </div>
          </label>
          <button className="button search-button" type="submit">
            <Search size={19} /> Search
          </button>
        </form>
      </section>

      <section className="shell section properties-section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">Handpicked homes</div>
            <h2>Stays with a sense of place</h2>
          </div>
          <span className="result-count">{properties.length} stays</span>
        </div>
        {preview && (
          <div className="preview-banner">
            Preview data is shown because the local API is offline. Start Docker Compose for live
            availability and booking actions.
          </div>
        )}
        {loading ? (
          <div className="property-grid skeleton-grid">
            {[1, 2, 3].map((item) => (
              <div className="skeleton-card" key={item} />
            ))}
          </div>
        ) : properties.length ? (
          <div className="property-grid">
            {properties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        ) : (
          <div className="empty-state">No stays match those dates yet. Try another city.</div>
        )}
      </section>

      <section className="engineering-section">
        <div className="shell">
          <div className="section-heading light-heading">
            <div>
              <div className="eyebrow">Engineering you can trust</div>
              <h2>Correctness behind every confirmation</h2>
            </div>
            <ArrowRight size={28} />
          </div>
          <div className="engineering-grid">
            <article>
              <DatabaseZap size={25} />
              <h3>Serialized reservations</h3>
              <p>Property-level locks stop simultaneous requests from creating overlapping stays.</p>
            </article>
            <article>
              <ShieldCheck size={25} />
              <h3>Server-owned pricing</h3>
              <p>Rates, totals, roles, and ownership are calculated from trusted database state.</p>
            </article>
            <article>
              <CalendarCheck2 size={25} />
              <h3>Verified reviews</h3>
              <p>Only the guest attached to a completed booking can review that property.</p>
            </article>
          </div>
        </div>
      </section>
    </main>
  );
}
