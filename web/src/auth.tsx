import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { api, loadTokens, saveTokens, setSessionLostHandler } from "./api";
import type { Me } from "./types";

type SessionResponse = { access_token: string; refresh_token: string; user: Me };

type AuthContextValue = {
  user: Me | null;
  loading: boolean;
  login: (login: string, password: string) => Promise<void>;
  signup: (data: { username: string; email: string; password: string; first_name: string; last_name: string }) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: Me) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(() => loadTokens() !== null);

  useEffect(() => {
    setSessionLostHandler(() => setUser(null));
    if (!loadTokens()) return;
    api
      .get<Me>("/me")
      .then(setUser)
      .catch(() => saveTokens(null))
      .finally(() => setLoading(false));
  }, []);

  const startSession = useCallback((data: SessionResponse) => {
    saveTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
    setUser(data.user);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      setUser,
      login: async (login, password) => startSession(await api.post<SessionResponse>("/auth/login", { login, password })),
      signup: async (data) => startSession(await api.post<SessionResponse>("/auth/signup", data)),
      logout: async () => {
        try {
          await api.post("/auth/logout");
        } finally {
          saveTokens(null);
          setUser(null);
        }
      },
    }),
    [user, loading, startSession],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
