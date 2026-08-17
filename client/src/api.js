// Central API service layer for AI Meeting Agent.
// Every function talks to the FastAPI backend. If the backend call fails
// (not running yet, network error, wrong URL) each function throws — callers
// decide whether to show an error or fall back to mock data.

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    let detail = "";
    try { detail = (await res.json()).detail || ""; } catch { /* ignore */ }
    throw new Error(`${options.method || "GET"} ${path} failed (${res.status}) ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ---- Meetings ----
// NOTE: confirm these paths/fields against backend/app/routes/meetings.py once shared.
export const getMeetings = () => request("/meetings");
export const getMeeting = (id) => request(`/meetings/${id}`);
export const createMeeting = (payload) => request("/meetings", { method: "POST", body: JSON.stringify(payload) });
export const processMeeting = (id) => request(`/meetings/${id}/process`, { method: "POST" });

// ---- Tasks ----
export const getTasks = () => request("/tasks");
export const createTask = (payload) => request("/tasks", { method: "POST", body: JSON.stringify(payload) });
export const updateTask = (id, payload) => request(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(payload) });

// ---- Assistant ----
export const askAssistant = (message) => request("/assistant", { method: "POST", body: JSON.stringify({ message }) });

// ---- MCP Memory ----
export const searchMemory = (query) => request(`/memory/search?q=${encodeURIComponent(query || "")}`);

// ---- Analytics ----
export const getAnalytics = () => request("/analytics");

// ---- Users ----
export const getCurrentUser = () => request("/users/me");
