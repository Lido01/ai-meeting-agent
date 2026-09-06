
import { apiRequest } from "./apiClient";

/**
 * Get all context continuity changes.
 */
export async function getContextChanges() {
  return apiRequest("/context-changes/");
}

/**
 * Get pending context continuity changes.
 */
export async function getPendingContextChanges() {
  return apiRequest("/context-changes/pending");
}

/**
 * Get a single context continuity change.
 */
export async function getContextChange(id) {
  return apiRequest(`/context-changes/${id}`);
}

/**
 * Confirm a detected context change.
 */
export async function confirmContextChange(id) {
  return apiRequest(`/context-changes/${id}/confirm`, {
    method: "POST",
  });
}

/**
 * Reject/keep the existing value for a context change.
 */
export async function rejectContextChange(id) {
  return apiRequest(`/context-changes/${id}/reject`, {
    method: "POST",
  });
}
