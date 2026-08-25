import React, { useState } from "react";
import ContextAlertModal from "../components/ContextAlertModal";

const initialAlerts = [
  {
    id: 1,
    type: "deadline",
    task: "Complete API integration",
    previousValue: "August 28, 2026",
    newValue: "September 3, 2026",
    sourceMeeting: "Weekly Team Meeting",
    meetingTimestamp: "August 24, 2026 • 4:20 PM",
    confidence: 0.94,
    status: "pending",
  },
  {
    id: 2,
    type: "owner",
    task: "Prepare frontend demo",
    previousValue: "Rahma",
    newValue: "Li_do",
    sourceMeeting: "Product Planning Meeting",
    meetingTimestamp: "August 23, 2026 • 6:10 PM",
    confidence: 0.91,
    status: "pending",
  },
  {
    id: 3,
    type: "decision",
    task: "Use Gemini Structured Outputs",
    previousValue: "Not confirmed",
    newValue: "Approved",
    sourceMeeting: "AI Architecture Meeting",
    meetingTimestamp: "August 22, 2026 • 8:30 PM",
    confidence: 0.97,
    status: "confirmed",
  },
];

function getTypeLabel(type) {
  if (type === "deadline") {
    return "Deadline Change";
  }

  if (type === "owner") {
    return "Owner Change";
  }

  if (type === "decision") {
    return "Decision Change";
  }

  return "Context Change";
}

function getTypeIcon(type) {
  if (type === "deadline") {
    return "📅";
  }

  if (type === "owner") {
    return "👤";
  }

  if (type === "decision") {
    return "✓";
  }

  return "🧠";
}

export default function ContextAlertsPage() {
  const [alerts, setAlerts] = useState(initialAlerts);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filter, setFilter] = useState("all");

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

  function confirmUpdate(id) {
    setAlerts((current) =>
      current.map((alert) =>
        alert.id === id
          ? {
              ...alert,
              status: "confirmed",
            }
          : alert
      )
    );

    setSelectedAlert(null);
  }

  function keepExisting(id) {
    setAlerts((current) =>
      current.map((alert) =>
        alert.id === id
          ? {
              ...alert,
              status: "dismissed",
            }
          : alert
      )
    );

    setSelectedAlert(null);
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

        <div className="context-alert-list">
          {filteredAlerts.length === 0 ? (
            <div className="context-empty-state">
              <div>✓</div>
              <h3>No alerts found</h3>
              <p>There are no alerts matching this filter.</p>
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
      </section>

      {selectedAlert && (
        <ContextAlertModal
          alert={selectedAlert}
          onConfirm={() => confirmUpdate(selectedAlert.id)}
          onKeepExisting={() => keepExisting(selectedAlert.id)}
          onClose={() => setSelectedAlert(null)}
        />
      )}
    </>
  );
}