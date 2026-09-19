import { ArrowRight, CheckCircle2, KeyRound, Mail, UserRound } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiClientError } from "../api";
import { useAuth } from "../auth";


export function AuthPage({ mode }: { mode: "login" | "register" }) {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [role, setRole] = useState<"GUEST" | "HOST">("GUEST");

  if (user) return <Navigate to="/dashboard" replace />;

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError("");
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(String(form.get("email")), String(form.get("password")));
      } else {
        await register({
          fullName: String(form.get("fullName")),
          email: String(form.get("email")),
          phone: String(form.get("phone") || ""),
          password: String(form.get("password")),
          role,
        });
      }
      const destination = (location.state as { from?: string } | null)?.from || "/dashboard";
      navigate(destination, { replace: true });
    } catch (caught) {
      setError(caught instanceof ApiClientError ? caught.message : "Could not reach StayEase");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-story">
        <div className="eyebrow">StayEase membership</div>
        <h1>{mode === "login" ? "Your next stay is waiting." : "Travel well. Host confidently."}</h1>
        <p>
          One account gives you transparent reservations, protected payments, and a clear history
          of every stay.
        </p>
        <div className="auth-benefits">
          <span>
            <CheckCircle2 /> Real-time availability checks
          </span>
          <span>
            <CheckCircle2 /> Clear booking status and totals
          </span>
          <span>
            <CheckCircle2 /> Reviews tied to verified stays
          </span>
        </div>
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <div className="eyebrow">{mode === "login" ? "Welcome back" : "Create an account"}</div>
          <h2>{mode === "login" ? "Sign in to StayEase" : "Start your StayEase journey"}</h2>
          {mode === "register" && (
            <div className="role-toggle">
              <button
                className={role === "GUEST" ? "active" : ""}
                type="button"
                onClick={() => setRole("GUEST")}
              >
                I’m travelling
              </button>
              <button
                className={role === "HOST" ? "active" : ""}
                type="button"
                onClick={() => setRole("HOST")}
              >
                I’m hosting
              </button>
            </div>
          )}
          <form className="stack-form" onSubmit={submit}>
            {mode === "register" && (
              <label>
                Full name
                <div className="field-with-icon bordered-field">
                  <UserRound size={18} />
                  <input name="fullName" required maxLength={100} placeholder="Your name" />
                </div>
              </label>
            )}
            <label>
              Email address
              <div className="field-with-icon bordered-field">
                <Mail size={18} />
                <input name="email" type="email" required placeholder="you@example.com" />
              </div>
            </label>
            {mode === "register" && (
              <label>
                Phone <span className="optional">optional</span>
                <input className="plain-input" name="phone" placeholder="+91 90000 00000" />
              </label>
            )}
            <label>
              Password
              <div className="field-with-icon bordered-field">
                <KeyRound size={18} />
                <input name="password" type="password" required minLength={8} />
              </div>
            </label>
            {error && <div className="form-error">{error}</div>}
            <button className="button button-wide" type="submit" disabled={submitting}>
              {submitting ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
              {!submitting && <ArrowRight size={18} />}
            </button>
          </form>
          <div className="auth-switch">
            {mode === "login" ? "New to StayEase?" : "Already have an account?"}{" "}
            <Link to={mode === "login" ? "/register" : "/login"}>
              {mode === "login" ? "Create an account" : "Sign in"}
            </Link>
          </div>
          {mode === "login" && (
            <div className="demo-credentials">
              Demo guest: <code>guest@stayease.local</code> / <code>Guest123!</code>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
