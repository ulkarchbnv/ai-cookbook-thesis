import { createContext, useContext, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      setProfile(null);
      return;
    }

    const loadProfile = async () => {
      setProfileLoading(true);
      try {
        const data = await apiFetch("/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(data);
      } catch {
        
        localStorage.removeItem("token");
        setToken(null);
        setProfile(null);
      } finally {
        setProfileLoading(false);
      }
    };

    loadProfile();
  }, [token]);

  const login = (nextToken) => {
    localStorage.setItem("token", nextToken);
    setToken(nextToken);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setProfile(null);
  };

  const updateProfile = (nextProfile) => {
    setProfile(nextProfile);
  };

  return (
    <AuthContext.Provider
      value={{ token, profile, profileLoading, login, logout, updateProfile }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}