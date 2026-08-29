import React, { useCallback, useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import PageHeader from "../components/PageHeader";
import Alert from "../components/Alert";
import TaskList from "../features/tasks/TaskList";
import {
  deleteTask,
  getTasks,
  updateTask,
} from "../services/taskService";

export default function TasksPage({
  refreshKey,
  onDataChanged,
}) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getTasks();

      setTasks(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(
        `Could not load tasks: ${
          err?.message || "Unknown error"
        }`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks, refreshKey]);

  async function handleToggle(task) {
    try {
      setError("");
      setMessage("");

      const { status } = await updateTask(task);

      setMessage(
        status === "completed"
          ? "Task completed."
          : "Task reopened."
      );

      await loadTasks();

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setError(
        `Could not update task: ${
          err?.message || "Unknown error"
        }`
      );
    }
  }

  async function handleDelete(taskId) {
    if (!taskId) {
      setError("Task ID is missing.");
      return;
    }

    if (!window.confirm("Delete this task?")) {
      return;
    }

    try {
      setError("");
      setMessage("");

      await deleteTask(taskId);

      setMessage("Task deleted successfully.");

      await loadTasks();

      if (onDataChanged) {
        onDataChanged();
      }
    } catch (err) {
      setError(
        `Could not delete task: ${
          err?.message || "Unknown error"
        }`
      );
    }
  }

  return (
    <>
      <PageHeader
        title="Action Items"
        subtitle="Tasks extracted from your meetings"
      />

      {error && (
        <Alert
          type="error"
          onClose={() => setError("")}
        >
          {error}
        </Alert>
      )}

      {message && (
        <Alert
          type="success"
          onClose={() => setMessage("")}
        >
          {message}
        </Alert>
      )}

      <div className="panel">
        {loading ? (
          <Loading />
        ) : tasks.length === 0 ? (
          <EmptyState
            icon="✓"
            title="No action items"
            text="Tasks generated from your meetings will appear here."
          />
        ) : (
          <TaskList
            tasks={tasks}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        )}
      </div>
    </>
  );
}