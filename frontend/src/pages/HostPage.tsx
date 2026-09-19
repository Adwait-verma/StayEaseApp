import { Building2, CalendarPlus, IndianRupee, Plus, Sparkles } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import { ApiClientError, api } from "../api";
import { useAuth } from "../auth";
import { PropertyCard } from "../components/PropertyCard";
import type { Property } from "../types";


const futureDate = (offset: number) => {
  const value = new Date();
  value.setDate(value.getDate() + offset);
  return value.toISOString().slice(0, 10);
};

export function HostPage() {
  const { user } = useAuth();
  const [properties, setProperties] = useState<Property[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = () => {
    api
      .properties(new URLSearchParams({ perPage: "50" }))
      .then(({ items }) => setProperties(items.filter((item) => item.hostId === user?.id)))
      .catch(() => setProperties([]));
  };

  useEffect(load, [user?.id]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const response = await api.createProperty({
        title: form.get("title"),
        description: form.get("description"),
        addressLine: form.get("addressLine"),
        city: form.get("city"),
        country: "India",
        capacity: Number(form.get("capacity")),
        bedrooms: Number(form.get("bedrooms")),
        bathrooms: Number(form.get("bathrooms")),
        basePrice: Number(form.get("basePrice")),
      });
      await api.addAvailability(response.property.id, {
        startDate: String(form.get("startDate")),
        endDate: String(form.get("endDate")),
        pricePerNight: Number(form.get("basePrice")),
        note: "Host launch rate",
      });
      event.currentTarget.reset();
      setMessage(`${response.property.title} is live with bookable availability.`);
      setShowForm(false);
      load();
    } catch (caught) {
      setError(caught instanceof ApiClientError ? caught.message : "Could not publish property");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="shell section host-page">
      <div className="dashboard-heading">
        <div>
          <div className="eyebrow">Host workspace</div>
          <h1>Manage stays with confidence</h1>
          <p>Publish clear listings and control exactly when guests can reserve.</p>
        </div>
        <button className="button" onClick={() => setShowForm((value) => !value)}>
          <Plus size={18} /> Add a property
        </button>
      </div>

      <div className="host-metrics">
        <article>
          <Building2 />
          <div>
            <strong>{properties.length}</strong>
            <span>active listings</span>
          </div>
        </article>
        <article>
          <CalendarPlus />
          <div>
            <strong>Live</strong>
            <span>availability rules</span>
          </div>
        </article>
        <article>
          <IndianRupee />
          <div>
            <strong>Server-side</strong>
            <span>price calculation</span>
          </div>
        </article>
      </div>

      {message && <div className="success-banner">{message}</div>}
      {error && <div className="form-error">{error}</div>}

      {showForm && (
        <section className="host-form-card">
          <div>
            <div className="eyebrow">
              <Sparkles size={15} /> New listing
            </div>
            <h2>Tell guests what makes it special</h2>
          </div>
          <form className="host-form" onSubmit={submit}>
            <label className="span-two">
              Property title
              <input name="title" required maxLength={150} placeholder="Cedar House by the Lake" />
            </label>
            <label className="span-two">
              Description
              <textarea
                name="description"
                required
                rows={4}
                placeholder="Describe the experience, setting, and what guests will love."
              />
            </label>
            <label>
              Address
              <input name="addressLine" required placeholder="Street address" />
            </label>
            <label>
              City
              <input name="city" required placeholder="Goa" />
            </label>
            <label>
              Guests
              <input name="capacity" type="number" min="1" max="50" defaultValue="2" required />
            </label>
            <label>
              Bedrooms
              <input name="bedrooms" type="number" min="1" max="30" defaultValue="1" required />
            </label>
            <label>
              Bathrooms
              <input name="bathrooms" type="number" min="0.5" step="0.5" defaultValue="1" required />
            </label>
            <label>
              Nightly price
              <input name="basePrice" type="number" min="1" defaultValue="3500" required />
            </label>
            <label>
              Available from
              <input name="startDate" type="date" min={futureDate(1)} defaultValue={futureDate(1)} required />
            </label>
            <label>
              Available until
              <input name="endDate" type="date" min={futureDate(2)} defaultValue={futureDate(180)} required />
            </label>
            <div className="span-two form-actions">
              <button className="button-secondary" type="button" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button className="button" type="submit" disabled={busy}>
                {busy ? "Publishing…" : "Publish property and availability"}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="section compact-section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">Your portfolio</div>
            <h2>Published properties</h2>
          </div>
        </div>
        {properties.length ? (
          <div className="property-grid">
            {properties.map((property) => (
              <PropertyCard key={property.id} property={property} />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <Building2 size={34} />
            <h2>Your first listing starts here</h2>
            <p>Publish a property with a future availability window to make it searchable.</p>
          </div>
        )}
      </section>
    </main>
  );
}
