import {
  createContext,
  type PropsWithChildren,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { api } from "./api";
import type { User } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    fullName: string;
    email: string;
    password: string;
    phone?: string;
    role: "GUEST" | "HOST";
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionStorage.getItem("stayease_token")) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then(({ user: currentUser }) => setUser(currentUser))
      .catch(() => sessionStorage.removeItem("stayease_token"))
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      async login(email, password) {
        const response = await api.login(email, password);
        sessionStorage.setItem("stayease_token", response.token);
        setUser(response.user);
      },
      async register(payload) {
        const response = await api.register(payload);
        sessionStorage.setItem("stayease_token", response.token);
        setUser(response.user);
      },
      logout() {
        sessionStorage.removeItem("stayease_token");
        setUser(null);
      },
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// The provider and hook intentionally share one small module.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
