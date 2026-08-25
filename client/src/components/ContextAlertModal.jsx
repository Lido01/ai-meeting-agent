import React from "react";

export default function ContextAlertModal({
  alert,
  onConfirm,
  onKeepExisting,
  onClose,
}) {
  if (!alert) {
    return null;
  }

  return (
    <div className="context-modal-overlay" onClick={onClose}>
      <div
        className="context-alert-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="context-modal-header">
          <div className="context-warning-icon">⚠️</div>

          <div>
            <span className="context-alert-label">
              Context Continuity Alert
            </span>

            <h2>Change detected</h2>
          </div>

          <button
            type="button"
            className="context-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="context-alert-message">
          This information has changed compared with a previous meeting.
          Please confirm before updating the task.
        </div>

        <div className="context-task-box">
          <span className="context-task-label">TASK</span>
          <strong>{alert.task}</strong>
        </div>

        <div className="context-change-box">
          <div className="context-change-column">
            <span className="context-change-label">PREVIOUS</span>

            <strong className="context-old-value">
              {alert.previousValue}
            </strong>
          </div>

          <div className="context-change-arrow">→</div>

          <div className="context-change-column">
            <span className="context-change-label">NEW</span>

            <strong className="context-new-value">
              {alert.newValue}
            </strong>
          </div>
        </div>

        <div className="context-source-box">
          <div>
            <span>Source meeting</span>
            <strong>{alert.sourceMeeting}</strong>
          </div>

          <div>
            <span>Meeting timestamp</span>
            <strong>{alert.meetingTimestamp}</strong>
          </div>

          {alert.confidence && (
            <div>
              <span>Detection confidence</span>
              <strong>{Math.round(alert.confidence * 100)}%</strong>
            </div>
          )}
        </div>

        <div className="context-info-message">
          <span>🧠</span>

          <p>
            This change was detected from previous meeting context. Your
            confirmation is required before the task is updated.
          </p>
        </div>

        <div className="context-modal-actions">
          <button
            type="button"
            className="secondary-button context-keep-button"
            onClick={onKeepExisting}
          >
            Keep Existing
          </button>

          <button
            type="button"
            className="primary-button context-confirm-button"
            onClick={onConfirm}
          >
            ✓ Confirm Update
          </button>
        </div>
      </div>
    </div>
  );
}