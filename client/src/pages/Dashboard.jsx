import React, { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Loading from "../components/Loading";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import { getMeetings, getMeeting } from "../services/meetingService";
import { getTasks, updateTask } from "../services/taskService";
import TaskList from "../features/tasks/TaskList";

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

function getTaskStatus(task) {
  return task?.status || (task?.completed ? "completed" : "open");
}

export default function Dashboard({
  onNavigate,
  onOpenMeeting,
  refreshKey,
  onError,
}) {
  const [meetings, setMeetings] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        setLoading(true);

        const [meetingData, taskData] = await Promise.all([
          getMeetings(),
          getTasks(),
        ]);

        if (!mounted) return;

        setMeetings(Array.isArray(meetingData) ? meetingData : []);
        setTasks(Array.isArray(taskData) ? taskData : []);
      } catch (error) {
        if (mounted) {
          const message =
            error?.message || "Unable to load dashboard data.";

          if (onError) {
            onError(`Could not load dashboard data: ${message}`);
          }
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      mounted = false;
    };
  }, [refreshKey, onError]);

  const completedTasks = tasks.filter(
    (task) => getTaskStatus(task) === "completed"
  ).length;

  const pendingTasks = tasks.length - completedTasks;

  async function handleOpenMeeting(id) {
    if (!id) {
      if (onError) {
        onError("Meeting ID is missing.");
      }
      return;
    }

    try {
      const meeting = await getMeeting(id);
      onOpenMeeting(meeting);
    } catch (error) {
      if (onError) {
        onError(
          `Could not load meeting: ${
            error?.message || "Unknown error"
          }`
        );
      }
    }
  }

  async function handleToggleTask(task) {
    try {
      const { status } = await updateTask(task);

      setTasks((current) =>
        current.map((item) => {
          const itemId = item?.id || item?.task_id;
          const taskId = task?.id || task?.task_id;

          if (itemId !== taskId) {
            return item;
          }

          return {
            ...item,
            status,
            completed: status === "completed",
          };
        })
      );
    } catch (error) {
      if (onError) {
        onError(
          `Could not update task: ${
            error?.message || "Unknown error"
          }`
        );
      }
    }
  }

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Your AI-powered meeting workspace"
      />

      <div className="stats-grid">
        <StatCard
          icon="📊"
          title="Total Meetings"
          value={meetings.length}
          onClick={() => onNavigate("meetings")}
        />

        <StatCard
          icon="✓"
          title="Completed Tasks"
          value={completedTasks}
          onClick={() => onNavigate("tasks")}
        />

        <StatCard
          icon="◷"
          title="Pending Tasks"
          value={pendingTasks}
          onClick={() => onNavigate("tasks")}
        />

        <StatCard
          icon="🤖"
          title="AI Assistant"
          value="Ready"
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Recent Meetings</h2>
              <p>Your latest meetings</p>
            </div>

            <button
              type="button"
              className="text-button"
              onClick={() => onNavigate("meetings")}
            >
              View all →
            </button>
          </div>

          {loading ? (
            <Loading />
          ) : meetings.length === 0 ? (
            <EmptyState
              icon="📊"
              title="No meetings yet"
              text="Create or upload your first meeting."
            />
          ) : (
            <div className="meeting-list">
              {meetings.slice(0, 5).map((meeting, index) => {
                const meetingId =
                  meeting?.id || meeting?.meeting_id;

                return (
                  <div
                    className="meeting-item"
                    key={meetingId || index}
                    onClick={() =>
                      handleOpenMeeting(meetingId)
                    }
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter" ||
                        event.key === " "
                      ) {
                        handleOpenMeeting(meetingId);
                      }
                    }}
                  >
                    <div className="meeting-icon">
                      🎙️
                    </div>

                    <div className="meeting-info">
                      <strong>
                        {getMeetingTitle(meeting)}
                      </strong>

                      <span>
                        {getMeetingDescription(meeting).slice(
                          0,
                          90
                        )}
                      </span>
                    </div>

                    <span className="arrow">›</span>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Action Items</h2>
              <p>Tasks extracted from meetings</p>
            </div>

            <button
              type="button"
              className="text-button"
              onClick={() => onNavigate("tasks")}
            >
              View all →
            </button>
          </div>

          {loading ? (
            <Loading />
          ) : tasks.length === 0 ? (
            <EmptyState
              icon="✓"
              title="No tasks yet"
              text="AI-generated action items will appear here."
            />
          ) : (
            <TaskList
              tasks={tasks.slice(0, 5)}
              compact
              onToggle={handleToggleTask}
              onDelete={() => onNavigate("tasks")}
            />
          )}
        </section>
      </div>
    </>
  );
}