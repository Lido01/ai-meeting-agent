import React from "react";

function getMeetingTitle(meeting) {
  return (
    meeting?.title ||
    meeting?.name ||
    meeting?.meeting_title ||
    "Untitled Meeting"
  );
}

function getMeetingDescription(meeting) {
  return String(
    meeting?.summary_text ||
      meeting?.summary ||
      meeting?.transcript_text ||
      meeting?.transcript ||
      meeting?.description ||
      "No description available."
  );
}

export default function MeetingList({ meetings = [], onOpen }) {
  return (
    <div className="meeting-cards">
      {meetings.map((meeting, index) => {
        const meetingId = meeting?.id || meeting?.meeting_id;

        return (
          <div
            className="meeting-card"
            key={meetingId || index}
          >
            <div className="card-icon">🎙️</div>

            <h3>{getMeetingTitle(meeting)}</h3>

            <p>
              {getMeetingDescription(meeting).slice(0, 150)}
            </p>

            <div className="card-footer">
              <span>
                {meeting?.created_at
                  ? new Date(
                      meeting.created_at
                    ).toLocaleDateString()
                  : "Meeting"}
              </span>

              <button
                type="button"
                className="text-button"
                onClick={() => onOpen?.(meetingId)}
              >
                Open →
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}