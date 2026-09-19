import { Building2, CalendarDays, LogOut, Menu, ShieldCheck, UserRound } from "lucide-react";
import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../auth";


export function Header() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const isHost = user?.roles.includes("HOST");
  const isAdmin = user?.roles.includes("ADMIN");

  return (
    <header className="site-header">
      <div className="shell nav-shell">
        <Link className="brand" to="/" onClick={() => setOpen(false)}>
          <span className="brand-mark">S</span>
          <span>StayEase</span>
        </Link>
        <button
          className="menu-button"
          type="button"
          aria-label="Toggle navigation"
          onClick={() => setOpen((value) => !value)}
        >
          <Menu size={22} />
        </button>
        <nav className={open ? "nav-links nav-links-open" : "nav-links"}>
          <NavLink to="/" onClick={() => setOpen(false)}>
            Explore
          </NavLink>
          {user && (
            <NavLink to="/dashboard" onClick={() => setOpen(false)}>
              <CalendarDays size={17} /> Trips
            </NavLink>
          )}
          {isHost && (
            <NavLink to="/host" onClick={() => setOpen(false)}>
              <Building2 size={17} /> Host
            </NavLink>
          )}
          {isAdmin && (
            <NavLink to="/admin" onClick={() => setOpen(false)}>
              <ShieldCheck size={17} /> Operations
            </NavLink>
          )}
          {user ? (
            <div className="profile-menu">
              <span className="profile-name">
                <UserRound size={17} /> {user.fullName.split(" ")[0]}
              </span>
              <button type="button" className="link-button" onClick={logout}>
                <LogOut size={16} /> Sign out
              </button>
            </div>
          ) : (
            <>
              <NavLink to="/login" onClick={() => setOpen(false)}>
                Sign in
              </NavLink>
              <Link className="button button-small" to="/register" onClick={() => setOpen(false)}>
                Join StayEase
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
