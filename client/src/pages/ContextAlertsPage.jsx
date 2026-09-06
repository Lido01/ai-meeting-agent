import React, { useCallback, useEffect, useState } from "react";
import ContextAlertModal from "../components/ContextAlertModal";
import Alert from "../components/Alert";
import Loading from "../components/Loading";
import {
  getContextChanges,
  confirmContextChange,
  rejectContextChange,
} from "../services/contextChangeService";
import { getTasks } from "../services/taskService";
import { getMeetings } from "../services/meetingService";

function getTypeLabel(type) {
  if (type === "deadline") {
    return "Deadline Change";
  }

  if (type === "owner" || type === "assignee") {
    return "Owner Change";
  }

  if (type === "decision") {
    return "Decision Change";
  }

  return "Context Change";
}

function getTypeIcon(type) {
  if (type === "deadline") {
    return "";
  }

  if (type === "owner" || type === "assignee") {
    return "";
  }

  if (type === "decision") {
    return "";
  }

  return "";
}

function formatTimestamp(value) {
  if (!value) {
    return "Unknown time";
  }

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }

  return parsed.toLocaleString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

// Combine a raw ContextChange record from the backend with the task and
// meeting it references, so the UI can show a task name / source meeting
// the same way the original design did — without fabricating any data
// the backend does not actually provide (e.g. a confidence score).
function enrichChange(change, tasksById, meetingsById) {
  const relatedTask = change.task_id
    ? tasksById.get(change.task_id)
    : null;

  const sourceMeeting = change.meeting_id
    ? meetingsById.get(change.meeting_id)
    : null;

  return {
    id: change.id,
    type: change.change_type,
    task:
      relatedTask?.description ||
      change.task ||
      "General meeting update",
    previousValue: change.previous_value ?? "Not previously recorded",
    newValue: change.new_value ?? "Unknown",
    evidence: change.evidence || "",
    sourceMeeting: sourceMeeting?.title || "Unknown meeting",
    meetingTimestamp: formatTimestamp(sourceMeeting?.created_at),
    status: change.status,
  };
}

export default function ContextAlertsPage({ refreshKey, onDataChanged }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [filter, setFilter] = useState("all");

  const loadAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const [changes, tasks, meetings] = await Promise.all([
        getContextChanges(),
        getTasks(),
        getMeetings(),
      ]);

      const tasksById = new Map(
        (Array.isArray(tasks) ? tasks : []).map((task) => [
          task.id,
          task,
        ])
      );

      const meetingsById = new Map(
        (Array.isArray(meetings) ? meetings : []).map((meeting) => [
          meeting.id,
          meeting,
        ])
      );

      const enriched = (Array.isArray(changes) ? changes : []).map(
        (change) => enrichChange(change, tasksById, meetingsById)
      );

      setAlerts(enriched);
    } catch (err) {
      setError(
        `Could not load context alerts: ${
          err?.message || "Unknown error"
        }`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts, refreshKey]);

  const pendingCount = alerts.filter(
    (alert) => alert.status === "pending"
  ).length;

  const confirmedCount = alerts.filter(
    (alert) => alert.status === "confirmed"
  ).length;

  const filteredAlerts =
    filter === "all"
      ? alerts
      : alerts.filter((alert) => alert.status === filter);

  async function confirmUpdate(id) {
    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      await confirmContextChange(id);

      setMessage("Context change confirmed and task updated.");
      setSelectedAlert(null);

      await loadAlerts();

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setError(
        `Could not confirm context change: ${
          err?.message || "Unknown error"
        }`
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function keepExisting(id) {
    try {
      setActionLoading(true);
      setError("");
      setMessage("");

      await rejectContextChange(id);

      setMessage("Existing value kept. The task was not changed.");
      setSelectedAlert(null);

      await loadAlerts();

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setError(
        `Could not update context change: ${
          err?.message || "Unknown error"
        }`
      );
    } finally {
      setActionLoading(false);
    }
  }

  function openAlert(alert) {
    setSelectedAlert(alert);
  }

  return (
    <>
      <div className="page-header context-page-header">
        <div>
          <div className="context-page-eyebrow">
            🧠 MCP Context Continuity
          </div>

          <h1>Context Alerts</h1>

          <p>
            Review changes detected between your current and previous
            meetings.
          </p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => {
            const firstPending = alerts.find(
              (alert) => alert.status === "pending"
            );

            if (firstPending) {
              setSelectedAlert(firstPending);
            }
          }}
        >
          ⚠ Review Alerts
        </button>
      </div>

      {error && (
        <Alert type="error" onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {message && (
        <Alert type="success" onClose={() => setMessage("")}>
          {message}
        </Alert>
      )}

      <section className="context-hero panel">
        <div className="context-hero-icon">🧠</div>

        <div className="context-hero-content">
          <span>Context Continuity</span>

          <h2>Your meetings remember what happened before.</h2>

          <p>
            Meeting AI compares new decisions, deadlines, and owners with
            previous meeting context and asks for confirmation before changing
            your tasks.
          </p>
        </div>

        <div className="context-hero-status">
          <span className="context-live-dot">●</span>
          Context monitoring active
        </div>
      </section>

      <section className="context-stats">
        <article className="panel context-stat-card">
          <span className="context-stat-icon warning">⚠️</span>

          <div>
            <span>Pending confirmation</span>
            <strong>{pendingCount}</strong>
          </div>
        </article>

        <article className="panel context-stat-card">
          <span className="context-stat-icon success">✓</span>

          <div>
            <span>Confirmed updates</span>
            <strong>{confirmedCount}</strong>
          </div>
        </article>

        <article className="panel context-stat-card">
          <span className="context-stat-icon brain">🧠</span>

          <div>
            <span>Total context alerts</span>
            <strong>{alerts.length}</strong>
          </div>
        </article>
      </section>

      <section className="panel context-alerts-panel">
        <div className="context-alerts-toolbar">
          <div>
            <h2>Detected Changes</h2>
            <p>
              Changes found by comparing current meeting context with
              previous meetings.
            </p>
          </div>

          <div className="context-filters">
            <button
              type="button"
              className={
                filter === "all"
                  ? "context-filter active"
                  : "context-filter"
              }
              onClick={() => setFilter("all")}
            >
              All
            </button>

            <button
              type="button"
              className={
                filter === "pending"
                  ? "context-filter active"
                  : "context-filter"
              }
              onClick={() => setFilter("pending")}
            >
              Pending
            </button>

            <button
              type="button"
              className={
                filter === "confirmed"
                  ? "context-filter active"
                  : "context-filter"
              }
              onClick={() => setFilter("confirmed")}
            >
              Confirmed
            </button>
          </div>
        </div>

        {loading ? (
          <Loading />
        ) : (
          <div className="context-alert-list">
            {filteredAlerts.length === 0 ? (
              <div className="context-empty-state">
                <div>✓</div>
                <h3>No alerts found</h3>
                <p>
                  {alerts.length === 0
                    ? "Upload and process a meeting to start detecting context changes."
                    : "There are no alerts matching this filter."}
                </p>
              </div>
            ) : (
              filteredAlerts.map((alert) => (
                <article
                  className={`context-alert-card ${
                    alert.status !== "pending"
                      ? "context-alert-resolved"
                      : ""
                  }`}
                  key={alert.id}
                >
                  <div
                    className={`context-alert-type-icon ${alert.type}`}
                  >
                    {getTypeIcon(alert.type)}
                  </div>

                  <div className="context-alert-card-content">
                    <div className="context-alert-card-top">
                      <div>
                        <span className="context-alert-type">
                          {getTypeLabel(alert.type)}
                        </span>

                        <h3>{alert.task}</h3>
                      </div>

                      <span
                        className={`context-status ${
                          alert.status === "pending"
                            ? "pending"
                            : alert.status === "confirmed"
                            ? "confirmed"
                            : "dismissed"
                        }`}
                      >
                        {alert.status === "pending"
                          ? "Needs confirmation"
                          : alert.status === "confirmed"
                          ? "Confirmed"
                          : "Kept existing"}
                      </span>
                    </div>

                    <div className="context-values">
                      <div>
                        <span>Previous</span>
                        <strong>{alert.previousValue}</strong>
                      </div>

                      <div className="context-small-arrow">→</div>

                      <div>
                        <span>New</span>
                        <strong>{alert.newValue}</strong>
                      </div>
                    </div>

                    <div className="context-alert-footer">
                      <div className="context-meeting-info">
                        <span>🎥</span>

                        <div>
                          <strong>{alert.sourceMeeting}</strong>
                          <small>{alert.meetingTimestamp}</small>
                        </div>
                      </div>

                      {alert.status === "pending" && (
                        <button
                          type="button"
                          className="primary-button context-review-button"
                          onClick={() => openAlert(alert)}
                        >
                          Review Change
                        </button>
                      )}
                    </div>
                  </div>
                </article>
              ))
            )}
          </div>
        )}
      </section>

      {selectedAlert && (
        <ContextAlertModal
          alert={selectedAlert}
          onConfirm={() =>
            !actionLoading && confirmUpdate(selectedAlert.id)
          }
          onKeepExisting={() =>
            !actionLoading && keepExisting(selectedAlert.id)
          }
          onClose={() => {
            if (!actionLoading) {
              setSelectedAlert(null);
            }
          }}
        />
      )}
    </>
  );
}
