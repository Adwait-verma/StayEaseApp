import type { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../auth";
import type { Role } from "../types";


export function ProtectedRoute({
  children,
  roles,
}: PropsWithChildren<{ roles?: Role[] }>) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="page-loader">Preparing your stay…</div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !user.roles.some((role) => roles.includes(role))) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
