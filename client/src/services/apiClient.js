export const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const TOKEN_KEY = "meeting_ai_token";

export async function apiRequest(url, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  const headers = {
    ...(options.headers || {}),
  };

  // Don't manually set Content-Type for FormData.
  // The browser adds the correct multipart boundary automatically.
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    });
  } catch (error) {
    console.error("API connection error:", error);

    throw new Error(
      `Cannot connect to the backend. Make sure FastAPI is running at ${API_BASE}.`
    );
  }

  const contentType = response.headers.get("content-type");

  let data = null;

  try {
    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch (error) {
    console.error("Failed to parse API response:", error);
  }

  // JWT expired/invalid
  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);

    window.dispatchEvent(new Event("auth-expired"));

    throw new Error("Your session has expired. Please sign in again.");
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data
        ? data.detail || JSON.stringify(data)
        : data;

    throw new Error(
      detail || `Request failed with status ${response.status}`
    );
  }

  return data;
}

export async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE}/openapi.json`);

    return response.ok;
  } catch (error) {
    console.error("Backend health check failed:", error);

    return false;
  }
}