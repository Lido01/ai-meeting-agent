const MEET_1 =
  "Rahma is assigned to implement JWT authentication with a deadline of September 10.";

const MEET_2 =
  "Ali is now responsible for implementing JWT authentication. The deadline has been changed to September 15.";

function normalize(text) {
  return String(text || "").toLowerCase();
}

export function getDemoMeetingMemoryReply(message) {
  const text = normalize(message);

  if (!text) {
    return null;
  }

  const asksWhatChanged =
    text.includes("what changed") ||
    text.includes("between the meetings") ||
    text.includes("between meetings");

  const asksWhoNow =
    text.includes("who is responsible") ||
    text.includes("who is assigned") ||
    text.includes("responsible for it") ||
    text.includes("who owns");

  const asksAuthDecision =
    text.includes("authentication") ||
    text.includes("jwt") ||
    (text.includes("decided") && text.includes("task"));

  if (asksWhatChanged) {
    return {
      reply:
        "The owner changed from Rahma to Ali, and the deadline moved from September 10 to September 15.",
      contextLabel: "Context retrieved from MEET_1 and MEET_2",
    };
  }

  if (asksWhoNow) {
    return {
      reply:
        "In the latest meeting, the responsibility changed from Rahma to Ali, and the deadline was moved to September 15.",
      contextLabel: "Context retrieved from MEET_2",
    };
  }

  if (asksAuthDecision) {
    return {
      reply:
        "Based on our previous meeting, Rahma was assigned to implement JWT authentication with a deadline of September 10.",
      contextLabel: "Context retrieved from MEET_1",
    };
  }

  return null;
}

export const DEMO_MEETING_MEMORY = {
  MEET_1,
  MEET_2,
};
