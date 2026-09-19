import { Activity, Building2, IndianRupee, ShieldCheck, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api";
import type { AdminStats } from "../types";


const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .stats()
      .then(setStats)
      .catch(() => setError("Operational metrics are unavailable while the API is offline."));
  }, []);

  return (
    <main className="admin-page">
      <section className="admin-hero">
        <div className="shell">
          <div className="eyebrow">
            <ShieldCheck size={16} /> Marketplace operations
          </div>
          <h1>StayEase control centre</h1>
          <p>Monitor marketplace health without exposing guest or payment credentials.</p>
        </div>
      </section>
      <section className="shell section">
        {error && <div className="preview-banner">{error}</div>}
        <div className="admin-stat-grid">
          <article>
            <UsersRound />
            <span>Registered users</span>
            <strong>{stats?.users ?? "—"}</strong>
          </article>
          <article>
            <Building2 />
            <span>Active properties</span>
            <strong>{stats?.activeProperties ?? "—"}</strong>
          </article>
          <article>
            <Activity />
            <span>Total bookings</span>
            <strong>{stats?.bookings ?? "—"}</strong>
          </article>
          <article>
            <IndianRupee />
            <span>Paid booking value</span>
            <strong>{stats ? money.format(stats.paidRevenue) : "—"}</strong>
          </article>
        </div>
        <section className="operations-panel">
          <div>
            <div className="eyebrow">Booking lifecycle</div>
            <h2>Status distribution</h2>
          </div>
          <div className="status-bars">
            {Object.entries(stats?.bookingsByStatus || {}).map(([status, count]) => (
              <div key={status}>
                <span>{status.toLowerCase()}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${Math.max(8, (count / Math.max(stats?.bookings || 1, 1)) * 100)}%` }}
                  />
                </div>
                <strong>{count}</strong>
              </div>
            ))}
            {!stats && <div className="page-loader">Loading operational data…</div>}
          </div>
        </section>
      </section>
    </main>
  );
}
