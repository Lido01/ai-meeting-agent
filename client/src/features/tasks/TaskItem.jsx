import React from "react";

function getTaskTitle(task) {
  return (
    task?.title ||
    task?.task ||
    task?.description ||
    task?.name ||
    "Untitled Task"
  );
}

function getTaskStatus(task) {
  return String(
    task?.status || (task?.completed ? "completed" : "open")
  ).toLowerCase();
}

function getStatusLabel(status) {
  if (status === "completed") {
    return "Completed";
  }

  if (status === "in_progress" || status === "in progress") {
    return "In Progress";
  }

  return "Pending";
}

function getStatusClass(status) {
  if (status === "completed") {
    return "status-completed";
  }

  if (status === "in_progress" || status === "in progress") {
    return "status-progress";
  }

  return "status-pending";
}

function formatDueDate(value) {
  if (!value) {
    return null;
  }

  const raw = String(value);
  const parts = raw.match(/^(\d{4})-(\d{2})-(\d{2})/);

  const parsed = parts
    ? new Date(
        Number(parts[1]),
        Number(parts[2]) - 1,
        Number(parts[3])
      )
    : new Date(raw);

  if (Number.isNaN(parsed.getTime())) {
    return raw;
  }

  return parsed.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function getAssignee(task) {
  return task?.assigned_to || task?.assignee || "";
}

function getMeetingLabel(task) {
  return (
    task?.meeting_label ||
    task?.meeting_title ||
    task?.meeting ||
    task?.source_meeting ||
    ""
  );
}

export default function TaskItem({
  task,
  onToggle,
  onDelete,
  compact = false,
}) {
  const status = getTaskStatus(task);
  const completed = status === "completed";
  const taskId = task?.id || task?.task_id;
  const title = getTaskTitle(task);
  const dueDate = formatDueDate(task?.deadline || task?.due_date);
  const assignee = getAssignee(task);
  const meetingLabel = getMeetingLabel(task);

  if (!task) {
    return null;
  }

  if (compact) {
    return (
      <div className="task-item">
        <button
          type="button"
          className={`checkbox ${completed ? "checked" : ""}`}
          onClick={() => onToggle?.(task)}
        >
          {completed ? "✓" : ""}
        </button>

        <span className={completed ? "task-completed" : ""}>
          {title}
        </span>
      </div>
    );
  }

  return (
    <div className="full-task-item task-card">
      <button
        type="button"
        className={`checkbox ${completed ? "checked" : ""}`}
        onClick={() => onToggle?.(task)}
      >
        {completed ? "✓" : ""}
      </button>

      <div className="task-content">
        <strong className={completed ? "task-completed" : ""}>
          {title}
        </strong>

        {task.description && task.description !== title && (
          <p>{task.description}</p>
        )}

        <div className="task-meta">
          <span className={`status ${getStatusClass(status)}`}>
            {getStatusLabel(status)}
          </span>

          {dueDate && (
            <span className="task-meta-item">Due {dueDate}</span>
          )}

          {assignee && (
            <span className="task-meta-item">Assignee: {assignee}</span>
          )}

          {meetingLabel && (
            <span className="task-meta-item task-meeting">
              Meeting: {meetingLabel}
            </span>
          )}
        </div>
      </div>

      <button
        type="button"
        className="delete-button"
        onClick={() => onDelete?.(taskId)}
      >
        🗑
      </button>
    </div>
  );
}
