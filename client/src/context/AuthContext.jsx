import React, { createContext, useContext, useEffect, useState } from "react";
import {
  getStoredToken,
  loginUser,
  logoutUser,
} from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken);

  useEffect(() => {
    function handleAuthExpired() {
      logoutUser();
      setToken(null);
    }

    window.addEventListener("auth-expired", handleAuthExpired);

    return () => {
      window.removeEventListener("auth-expired", handleAuthExpired);
    };
  }, []);

  async function login(email, password) {
    const newToken = await loginUser(email, password);
    setToken(newToken);
    return newToken;
  }

  function logout() {
    logoutUser();
    setToken(null);
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        isAuthenticated: Boolean(token),
        login,
        logout,
      }}
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