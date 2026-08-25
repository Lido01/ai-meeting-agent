import React, { useEffect, useState } from "react";
import { checkBackend } from "../../services/apiClient";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendOnline, setBackendOnline] = useState(null);

  useEffect(() => {
    checkBackend().then(setBackendOnline);
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }

    if (!password) {
      setError("Password is required.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await login(email.trim(), password);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">🤖</div>
        <h1>Meeting AI</h1>
        <p className="login-subtitle">AI-powered meeting intelligence</p>

        <div className="login-welcome">
          <h2>Welcome back</h2>
          <p>Sign in to access your meetings and action items.</p>
        </div>

        {backendOnline === false && (
          <div className="login-backend-warning">
            Cannot connect to the backend. Start FastAPI first.
          </div>
        )}

        {backendOnline === true && (
          <div className="login-backend-success">
            ✓ Backend connected
          </div>
        )}

        {error && <div className="login-error">⚠ {error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="login-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="test@example.com"
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className="login-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="login-security">
          🔒 Authentication secured by the FastAPI backend.
        </div>
      </div>
    </div>
  );
}