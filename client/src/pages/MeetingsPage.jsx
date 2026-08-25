import React, { useCallback, useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import PageHeader from "../components/PageHeader";
import Alert from "../components/Alert";
import MeetingList from "../features/meetings/MeetingList";
import AudioUploader from "../features/meetings/AudioUploader";
import CreateMeetingForm from "../features/meetings/CreateMeetingForm";
import {
  createMeeting,
  getMeeting,
  getMeetings,
  uploadMeeting,
} from "../services/meetingService";
import { getTasks } from "../services/taskService";

export default function MeetingsPage({
  onOpenMeeting,
  refreshKey,
  onDataChanged,
}) {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Load meetings from the backend
  const loadMeetings = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMeetings();
      setMeetings(data);
    } catch (err) {
      setError(`Could not load meetings: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Reload meetings when refreshKey changes
  useEffect(() => {
    loadMeetings();
  }, [loadMeetings, refreshKey]);

  // Create a new meeting
  async function handleCreate(title, validationError) {
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      await createMeeting(title);

      setModal(null);
      setMessage("Meeting created successfully.");

      await loadMeetings();

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setError(`Could not create meeting: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  }

  // Upload and process a meeting recording
  async function handleUpload(title, file, validationError) {
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setActionLoading(true);
      setError("");
      setMessage("Uploading and processing meeting...");

      const data = await uploadMeeting(title, file);

      setModal(null);

      setMessage(
        data?.message || "Meeting uploaded and processed successfully."
      );

      // Refresh meetings and tasks after processing
      await Promise.all([loadMeetings(), getTasks()]);

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setMessage("");
      setError(
        `Upload failed: ${err.message || "Unknown upload error"}`
      );
    } finally {
      setActionLoading(false);
    }
  }

  // Open a specific meeting
  async function handleOpen(id) {
    if (!id) {
      setError("Meeting ID is missing.");
      return;
    }

    try {
      setError("");

      const meeting = await getMeeting(id);

      onOpenMeeting(meeting);
    } catch (err) {
      setError(`Could not load meeting: ${err.message}`);
    }
  }

  return (
    <>
      <PageHeader
        title="Meetings"
        subtitle="Manage your recorded meetings"
        actions={
          <>
            <button
              className="secondary-button"
              onClick={() => {
                setError("");
                setMessage("");
                setModal("upload");
              }}
            >
              ↑ Upload
            </button>

            <button
              className="primary-button"
              onClick={() => {
                setError("");
                setMessage("");
                setModal("create");
              }}
            >
              + New Meeting
            </button>
          </>
        }
      />

      {/* Error message */}
      {error && (
        <Alert type="error" onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Success message */}
      {message && (
        <Alert type="success" onClose={() => setMessage("")}>
          {message}
        </Alert>
      )}

      {/* Meetings content */}
      {loading ? (
        <Loading />
      ) : meetings.length === 0 ? (
        <div className="panel">
          <EmptyState
            icon="📊"
            title="No meetings found"
            text="Create a meeting or upload a recording to get started."
          />

          <div className="center-actions">
            <button
              className="primary-button"
              onClick={() => {
                setError("");
                setMessage("");
                setModal("create");
              }}
            >
              + Create Meeting
            </button>

            <button
              className="secondary-button"
              onClick={() => {
                setError("");
                setMessage("");
                setModal("upload");
              }}
            >
              ↑ Upload Meeting
            </button>
          </div>
        </div>
      ) : (
        <MeetingList meetings={meetings} onOpen={handleOpen} />
      )}

      {/* Create meeting modal */}
      {modal === "create" && (
        <div
          className="modal-backdrop"
          onClick={() => {
            if (!actionLoading) {
              setModal(null);
            }
          }}
        >
          <div
            className="modal"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Create New Meeting</h2>

            <CreateMeetingForm
              onSubmit={handleCreate}
              onCancel={() => setModal(null)}
              loading={actionLoading}
            />
          </div>
        </div>
      )}

      {/* Upload meeting modal */}
      {modal === "upload" && (
        <div
          className="modal-backdrop"
          onClick={() => {
            if (!actionLoading) {
              setModal(null);
            }
          }}
        >
          <div
            className="modal"
            onClick={(event) => event.stopPropagation()}
          >
            <h2>Upload Meeting</h2>

            <AudioUploader
              onSubmit={handleUpload}
              onCancel={() => setModal(null)}
              loading={actionLoading}
            />
          </div>
        </div>
      )}
    </>
  );
}