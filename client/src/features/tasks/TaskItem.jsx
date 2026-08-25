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
  return task?.status || (task?.completed ? "completed" : "open");
}

export default function TaskItem({
  task,
  onToggle,
  onDelete,
  compact = false,
}) {
  const completed = getTaskStatus(task) === "completed";
  const taskId = task?.id || task?.task_id;

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
          {getTaskTitle(task)}
        </span>
      </div>
    );
  }

  return (
    <div className="full-task-item">
      <button
        type="button"
        className={`checkbox ${completed ? "checked" : ""}`}
        onClick={() => onToggle?.(task)}
      >
        {completed ? "✓" : ""}
      </button>

      <div className="task-content">
        <strong className={completed ? "task-completed" : ""}>
          {getTaskTitle(task)}
        </strong>

        {task.description && task.description !== getTaskTitle(task) && (
          <p>{task.description}</p>
        )}

        <div className="task-meta">
          <span
            className={`status ${
              completed ? "status-completed" : "status-pending"
            }`}
          >
            {completed ? "Completed" : "Pending"}
          </span>

          {(task.deadline || task.due_date) && (
            <span>
              Due:{" "}
              {new Date(
                task.deadline || task.due_date
              ).toLocaleDateString()}
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