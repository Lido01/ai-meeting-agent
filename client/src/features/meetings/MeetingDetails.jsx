import React from "react";
import Detail from "../../components/Detail";

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

export default function MeetingDetails({ meeting, onBack }) {
  if (!meeting) return null;

  const transcript = meeting.transcript_text || meeting.transcript;
  const summary = meeting.summary_text || meeting.summary;

  return (
    <div className="meeting-details">
      <button className="back-button" onClick={onBack}>
        ← Back to meetings
      </button>

      <div className="panel">
        <div className="detail-icon">🎙️</div>

        <h1>{getMeetingTitle(meeting)}</h1>

        <p className="detail-description">
          {getMeetingDescription(meeting)}
        </p>

        <div className="detail-grid">
          <Detail
            label="Meeting ID"
            value={meeting.id || meeting.meeting_id || "—"}
          />

          <Detail
            label="Created"
            value={
              meeting.created_at
                ? new Date(meeting.created_at).toLocaleString()
                : "—"
            }
          />

          <Detail
            label="Status"
            value={meeting.status || "Available"}
          />
        </div>

        {transcript && (
          <div className="transcript">
            <h2>Transcript</h2>
            <div className="transcript-box">{transcript}</div>
          </div>
        )}

        {summary && (
          <div className="transcript">
            <h2>AI Summary</h2>
            <div className="transcript-box">{summary}</div>
          </div>
        )}
      </div>
    </div>
  );
}
