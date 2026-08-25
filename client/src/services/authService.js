import {
  apiRequest,
  API_BASE,
  TOKEN_KEY,
} from "./apiClient";

export async function loginUser(email, password) {
  if (!email?.trim()) {
    throw new Error("Email is required.");
  }

  if (!password) {
    throw new Error("Password is required.");
  }

  const formData = new URLSearchParams();

  // FastAPI OAuth2PasswordRequestForm expects:
  // username = email
  // password = password
  formData.append("username", email.trim());
  formData.append("password", password);

  let response;

  try {
    response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Accept: "application/json",
      },
      body: formData.toString(),
    });
  } catch {
    throw new Error(
      "Cannot connect to the backend. Make sure FastAPI is running."
    );
  }

  let data = null;

  try {
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch {
    data = null;
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Invalid email or password.");
    }

    const detail =
      typeof data === "object" && data
        ? data.detail || data.message
        : data;

    throw new Error(
      detail || `Login failed with status ${response.status}.`
    );
  }

  const token =
    typeof data === "string"
      ? data
      : data?.access_token ||
        data?.token ||
        data?.accessToken;

  if (!token) {
    throw new Error(
      "Login succeeded, but the backend did not return an access token."
    );
  }

  localStorage.setItem(TOKEN_KEY, token);

  return token;
}

export function logoutUser() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}