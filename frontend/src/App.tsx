import { Github, HeartHandshake } from "lucide-react";
import { lazy, Suspense } from "react";
import { Link, Route, Routes } from "react-router-dom";

import { Header } from "./components/Header";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminPage } from "./pages/AdminPage";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { HomePage } from "./pages/HomePage";
import { HostPage } from "./pages/HostPage";
import { PropertyPage } from "./pages/PropertyPage";

const ApiDocsPage = lazy(() => import("./pages/ApiDocsPage"));

function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell footer-grid">
        <div>
          <Link className="brand footer-brand" to="/">
            <span className="brand-mark">S</span>
            <span>StayEase</span>
          </Link>
          <p>A portfolio marketplace focused on booking correctness and thoughtful product design.</p>
        </div>
        <div>
          <strong>Explore</strong>
          <Link to="/">Properties</Link>
          <Link to="/register">Become a host</Link>
        </div>
        <div>
          <strong>Engineering</strong>
          <a href="https://github.com/Adwait-verma/StayEaseApp">
            <Github size={16} /> GitHub repository
          </a>
          <Link to="/api-docs">Interactive API docs</Link>
          <span>
            <HeartHandshake size={16} /> Built as a student project
          </span>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/properties/:id" element={<PropertyPage />} />
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route
          path="/api-docs"
          element={
            <Suspense fallback={<main className="page-loading">Loading API explorer…</main>}>
              <ApiDocsPage />
            </Suspense>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/host"
          element={
            <ProtectedRoute roles={["HOST"]}>
              <HostPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["ADMIN"]}>
              <AdminPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<HomePage />} />
      </Routes>
      <Footer />
    </div>
  );
}
