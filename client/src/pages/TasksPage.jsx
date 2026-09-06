import React, { useCallback, useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import PageHeader from "../components/PageHeader";
import Alert from "../components/Alert";
import TaskList from "../features/tasks/TaskList";
import { DEMO_ACTION_ITEMS } from "../data/demoActionItems";
import { getMeetings } from "../services/meetingService";
import {
  deleteTask,
  getTasks,
  updateTask,
} from "../services/taskService";

function getMeetingLabel(task, meetingsById) {
  if (task?.meeting_label || task?.meeting_title || task?.meeting) {
    return task.meeting_label || task.meeting_title || task.meeting;
  }

  const meeting = meetingsById.get(task?.meeting_id);

  if (meeting?.title) {
    return meeting.title;
  }

  if (task?.meeting_id) {
    return `MEET_${task.meeting_id}`;
  }

  return "";
}

function enrichTasks(tasks, meetings) {
  const meetingsById = new Map(
    (meetings || []).map((meeting) => [
      meeting.id ?? meeting.meeting_id,
      meeting,
    ])
  );

  return tasks.map((task) => ({
    ...task,
    meeting_label: getMeetingLabel(task, meetingsById),
  }));
}

export default function TasksPage({
  refreshKey,
  onDataChanged,
}) {
  const [tasks, setTasks] = useState([]);
  const [usingDemo, setUsingDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const [taskData, meetingData] = await Promise.all([
        getTasks(),
        getMeetings().catch(() => []),
      ]);

      const apiTasks = Array.isArray(taskData) ? taskData : [];

      if (apiTasks.length > 0) {
        setUsingDemo(false);
        setTasks(
          enrichTasks(
            apiTasks,
            Array.isArray(meetingData) ? meetingData : []
          )
        );
        return;
      }

      setUsingDemo(true);
      setTasks(DEMO_ACTION_ITEMS);
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
    if (task?.isDemo || usingDemo) {
      setTasks((current) =>
        current.map((item) => {
          if ((item.id || item.task_id) !== (task.id || task.task_id)) {
            return item;
          }

          const currentStatus = String(item.status || "pending").toLowerCase();
          const nextStatus =
            currentStatus === "completed" ? "pending" : "completed";

          return {
            ...item,
            status: nextStatus,
          };
        })
      );
      return;
    }

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

    if (usingDemo || String(taskId).startsWith("demo-")) {
      setTasks((current) =>
        current.filter((item) => (item.id || item.task_id) !== taskId)
      );
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
