import { apiRequest } from "./apiClient";

export async function getMeetings() {
  const data = await apiRequest("/meetings/");

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.meetings)) {
    return data.meetings;
  }

  return [];
}

export async function getMeeting(meetingId) {
  if (!meetingId) {
    throw new Error("Meeting ID is missing.");
  }

  return apiRequest(`/meetings/${meetingId}`);
}

export async function createMeeting(title) {
  const cleanTitle = title?.trim();

  if (!cleanTitle) {
    throw new Error("Meeting title is required.");
  }

  return apiRequest("/meetings/", {
    method: "POST",
    body: JSON.stringify({
      title: cleanTitle,
    }),
  });
}

export async function uploadMeeting(title, file) {
  const cleanTitle = title?.trim();

  if (!cleanTitle) {
    throw new Error("Meeting title is required.");
  }

  if (!file) {
    throw new Error("Please select a meeting recording.");
  }

  const formData = new FormData();

  // Must match the FastAPI upload parameter.
  formData.append("file", file);

  const encodedTitle = encodeURIComponent(cleanTitle);

  return apiRequest(
    `/meetings/upload?title=${encodedTitle}`,
    {
      method: "POST",
      body: formData,
    }
  );
}