import { apiRequest } from "./apiClient";

export async function sendAssistantMessage(message) {
  const cleanMessage = message?.trim();

  if (!cleanMessage) {
    throw new Error("Please enter a question.");
  }

  const data = await apiRequest("/assistant/chat", {
    method: "POST",
    body: JSON.stringify({
      message: cleanMessage,
    }),
  });

  if (typeof data?.reply === "string" && data.reply.trim()) {
    return data.reply.trim();
  }

  throw new Error(
    "I couldn't retrieve your previous meeting context right now. Please try again."
  );
}
