import React, { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";
const TOKEN_KEY = "meeting_ai_token";

/* ============================================================
   API
============================================================ */

async function apiRequest(url, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  const headers = {
    ...(options.headers || {}),
  };

  // Do NOT set Content-Type manually for FormData.
  // Browser must generate the multipart boundary.
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    });
  } catch (error) {
    throw new Error(
      "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000"
    );
  }

  const contentType = response.headers.get("content-type");

  let data;

  try {
    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch {
    data = null;
  }

  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    window.dispatchEvent(new Event("auth-expired"));

    throw new Error("Your session has expired. Please sign in again.");
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data
        ? data.detail || JSON.stringify(data)
        : data;

    throw new Error(
      detail || `Request failed with status ${response.status}`
    );
  }

  return data;
}

/* ============================================================
   LOGIN
============================================================ */

async function loginUser(email, password) {
  /*
   * FastAPI OAuth2PasswordRequestForm expects:
   *
   * username = email
   * password = password
   */

  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  let response;

  try {
    response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });
  } catch {
    throw new Error(
      "Cannot connect to the backend. Start FastAPI first."
    );
  }

  const contentType = response.headers.get("content-type");

  let data;

  try {
    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data
        ? data.detail || "Invalid email or password."
        : data || "Login failed.";

    throw new Error(detail);
  }

  const token =
    data?.access_token ||
    data?.token ||
    data?.accessToken;

  if (!token) {
    throw new Error(
      "Login succeeded, but the backend did not return an access token."
    );
  }

  localStorage.setItem(TOKEN_KEY, token);

  return token;
}

/* ============================================================
   APP
============================================================ */

function App() {
  const [token, setToken] = useState(
    () => localStorage.getItem(TOKEN_KEY)
  );

  const [activePage, setActivePage] = useState("dashboard");

  const [meetings, setMeetings] = useState([]);
  const [tasks, setTasks] = useState([]);

  const [loadingMeetings, setLoadingMeetings] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(false);

  const [selectedMeeting, setSelectedMeeting] = useState(null);

  const [showCreateMeeting, setShowCreateMeeting] = useState(false);
  const [showUploadMeeting, setShowUploadMeeting] = useState(false);

  const [meetingTitle, setMeetingTitle] = useState("");
  const [meetingDescription, setMeetingDescription] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  /* ============================================================
     AUTH
  ============================================================ */

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);

    setMeetings([]);
    setTasks([]);
    setSelectedMeeting(null);
    setActivePage("dashboard");

    setMessage("");
    setError("");
  }

  useEffect(() => {
    function handleAuthExpired() {
      logout();
    }

    window.addEventListener("auth-expired", handleAuthExpired);

    return () => {
      window.removeEventListener(
        "auth-expired",
        handleAuthExpired
      );
    };
  }, []);

  /* ============================================================
     LOAD MEETINGS
  ============================================================ */

  async function loadMeetings() {
    if (!token) return;

    try {
      setLoadingMeetings(true);
      setError("");

      const data = await apiRequest("/meetings/");

      if (Array.isArray(data)) {
        setMeetings(data);
      } else if (Array.isArray(data?.meetings)) {
        setMeetings(data.meetings);
      } else {
        setMeetings([]);
      }
    } catch (err) {
      console.error(err);
      setError(`Could not load meetings: ${err.message}`);
    } finally {
      setLoadingMeetings(false);
    }
  }

  /* ============================================================
     LOAD TASKS
  ============================================================ */

  async function loadTasks() {
    if (!token) return;

    try {
      setLoadingTasks(true);
      setError("");

      const data = await apiRequest("/tasks/");

      if (Array.isArray(data)) {
        setTasks(data);
      } else if (Array.isArray(data?.tasks)) {
        setTasks(data.tasks);
      } else {
        setTasks([]);
      }
    } catch (err) {
      console.error(err);
      setError(`Could not load tasks: ${err.message}`);
    } finally {
      setLoadingTasks(false);
    }
  }

  /* ============================================================
     INITIAL DATA
  ============================================================ */

  useEffect(() => {
    if (!token) return;

    loadMeetings();
    loadTasks();
  }, [token]);

  /* ============================================================
     CREATE MEETING
  ============================================================ */

  async function createMeeting(event) {
    event.preventDefault();

    if (!meetingTitle.trim()) {
      setError("Meeting title is required.");
      return;
    }

    try {
      setError("");
      setMessage("");

      await apiRequest("/meetings/", {
        method: "POST",
        body: JSON.stringify({
          title: meetingTitle.trim(),
        }),
      });

      setMeetingTitle("");
      setMeetingDescription("");
      setShowCreateMeeting(false);

      setMessage("Meeting created successfully.");

      await loadMeetings();
    } catch (err) {
      console.error(err);
      setError(`Could not create meeting: ${err.message}`);
    }
  }

  /* ============================================================
     UPLOAD MEETING
     
     IMPORTANT:
     FastAPI expects:
     
     POST /meetings/upload?title=...
     
     with:
     
     file = multipart/form-data
     
     Therefore title MUST be in the URL, not FormData.
  ============================================================ */

  async function uploadMeeting(event) {
    event.preventDefault();

    if (!selectedFile) {
      setError("Please select an audio or video file.");
      return;
    }

    if (!meetingTitle.trim()) {
      setError("Meeting title is required.");
      return;
    }

    try {
      setError("");
      setMessage("Uploading and processing meeting...");

      const formData = new FormData();

      // IMPORTANT:
      // Only the file belongs in multipart/form-data.
      formData.append("file", selectedFile);

      // FastAPI expects title as a QUERY parameter.
      const title = encodeURIComponent(
        meetingTitle.trim()
      );

      console.log(
        "Uploading meeting:",
        meetingTitle.trim()
      );

      console.log(
        "Selected file:",
        selectedFile.name,
        selectedFile.type,
        selectedFile.size
      );

      const data = await apiRequest(
        `/meetings/upload?title=${title}`,
        {
          method: "POST",
          body: formData,
        }
      );

      console.log("Upload response:", data);

      setSelectedFile(null);
      setMeetingTitle("");
      setShowUploadMeeting(false);

      setMessage(
        data?.message ||
          "Meeting uploaded and processed successfully."
      );

      await loadMeetings();
      await loadTasks();
    } catch (err) {
      console.error("Upload error:", err);

      setMessage("");

      setError(
        `Upload failed: ${
          err?.message || "Unknown upload error"
        }`
      );
    }
  }

  /* ============================================================
     OPEN MEETING
  ============================================================ */

  async function openMeeting(meetingId) {
    if (!meetingId) {
      setError("Meeting ID is missing.");
      return;
    }

    try {
      setError("");

      const meeting = await apiRequest(
        `/meetings/${meetingId}`
      );

      setSelectedMeeting(meeting);
    } catch (err) {
      console.error(err);
      setError(`Could not load meeting: ${err.message}`);
    }
  }

  /* ============================================================
     UPDATE TASK
  ============================================================ */

  async function toggleTask(task) {
    const taskId = task.id || task.task_id;

    if (!taskId) {
      setError("Task ID is missing.");
      return;
    }

    const currentStatus =
      task.status ||
      (task.completed ? "completed" : "open");

    const newStatus =
      currentStatus === "completed"
        ? "open"
        : "completed";

    try {
      setError("");

      await apiRequest(`/tasks/${taskId}`, {
        method: "PUT",
        body: JSON.stringify({
          ...task,
          status: newStatus,
          completed: newStatus === "completed",
        }),
      });

      await loadTasks();

      setMessage(
        newStatus === "completed"
          ? "Task completed."
          : "Task reopened."
      );
    } catch (err) {
      console.error(err);
      setError(`Could not update task: ${err.message}`);
    }
  }

  /* ============================================================
     DELETE TASK
  ============================================================ */

  async function deleteTask(taskId) {
    if (!taskId) {
      setError("Task ID is missing.");
      return;
    }

    if (!window.confirm("Delete this task?")) {
      return;
    }

    try {
      setError("");

      await apiRequest(`/tasks/${taskId}`, {
        method: "DELETE",
      });

      setMessage("Task deleted successfully.");

      await loadTasks();
    } catch (err) {
      console.error(err);
      setError(`Could not delete task: ${err.message}`);
    }
  }

  /* ============================================================
     NAVIGATION
  ============================================================ */

  function navigate(page) {
    setActivePage(page);
    setSelectedMeeting(null);
    setError("");
    setMessage("");
  }

  /* ============================================================
     HELPERS
  ============================================================ */

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
    return (
      task?.status ||
      (task?.completed ? "completed" : "open")
    );
  }

  /* ============================================================
     LOGIN SCREEN
  ============================================================ */

  if (!token) {
    return (
      <LoginScreen
        onLogin={(newToken) => {
          setToken(newToken);
          setActivePage("dashboard");
        }}
      />
    );
  }

  /* ============================================================
     DASHBOARD
  ============================================================ */

  function Dashboard() {
    const completedTasks = tasks.filter(
      (task) =>
        getTaskStatus(task) === "completed"
    ).length;

    const pendingTasks =
      tasks.length - completedTasks;

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
            onClick={() => navigate("meetings")}
          />

          <StatCard
            icon="✓"
            title="Completed Tasks"
            value={completedTasks}
            onClick={() => navigate("tasks")}
          />

          <StatCard
            icon="◷"
            title="Pending Tasks"
            value={pendingTasks}
            onClick={() => navigate("tasks")}
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
                className="text-button"
                onClick={() => navigate("meetings")}
              >
                View all →
              </button>
            </div>

            {loadingMeetings ? (
              <Loading />
            ) : meetings.length === 0 ? (
              <EmptyState
                icon="📊"
                title="No meetings yet"
                text="Create or upload your first meeting."
              />
            ) : (
              <div className="meeting-list">
                {meetings.slice(0, 5).map(
                  (meeting, index) => {
                    const meetingId =
                      meeting.id ||
                      meeting.meeting_id;

                    return (
                      <div
                        className="meeting-item"
                        key={
                          meetingId || index
                        }
                        onClick={() =>
                          openMeeting(meetingId)
                        }
                      >
                        <div className="meeting-icon">
                          🎙️
                        </div>

                        <div className="meeting-info">
                          <strong>
                            {getMeetingTitle(
                              meeting
                            )}
                          </strong>

                          <span>
                            {getMeetingDescription(
                              meeting
                            ).slice(0, 90)}
                          </span>
                        </div>

                        <span className="arrow">
                          ›
                        </span>
                      </div>
                    );
                  }
                )}
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
                className="text-button"
                onClick={() => navigate("tasks")}
              >
                View all →
              </button>
            </div>

            {loadingTasks ? (
              <Loading />
            ) : tasks.length === 0 ? (
              <EmptyState
                icon="✓"
                title="No tasks yet"
                text="AI-generated action items will appear here."
              />
            ) : (
              <div className="task-list">
                {tasks.slice(0, 5).map(
                  (task, index) => {
                    const completed =
                      getTaskStatus(task) ===
                      "completed";

                    return (
                      <div
                        className="task-item"
                        key={
                          task.id ||
                          task.task_id ||
                          index
                        }
                      >
                        <button
                          className={`checkbox ${
                            completed
                              ? "checked"
                              : ""
                          }`}
                          onClick={() =>
                            toggleTask(task)
                          }
                        >
                          {completed ? "✓" : ""}
                        </button>

                        <span
                          className={
                            completed
                              ? "task-completed"
                              : ""
                          }
                        >
                          {getTaskTitle(task)}
                        </span>
                      </div>
                    );
                  }
                )}
              </div>
            )}
          </section>
        </div>
      </>
    );
  }

  /* ============================================================
     MEETINGS
  ============================================================ */

  function MeetingsPage() {
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
                  setMeetingTitle("");
                  setSelectedFile(null);
                  setShowUploadMeeting(true);
                }}
              >
                ↑ Upload
              </button>

              <button
                className="primary-button"
                onClick={() =>
                  setShowCreateMeeting(true)
                }
              >
                + New Meeting
              </button>
            </>
          }
        />

        {loadingMeetings ? (
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
                onClick={() =>
                  setShowCreateMeeting(true)
                }
              >
                + Create Meeting
              </button>

              <button
                className="secondary-button"
                onClick={() => {
                  setMeetingTitle("");
                  setSelectedFile(null);
                  setShowUploadMeeting(true);
                }}
              >
                ↑ Upload Meeting
              </button>
            </div>
          </div>
        ) : (
          <div className="meeting-cards">
            {meetings.map((meeting, index) => {
              const meetingId =
                meeting.id ||
                meeting.meeting_id;

              return (
                <div
                  className="meeting-card"
                  key={meetingId || index}
                >
                  <div className="card-icon">
                    🎙️
                  </div>

                  <h3>
                    {getMeetingTitle(meeting)}
                  </h3>

                  <p>
                    {getMeetingDescription(
                      meeting
                    ).slice(0, 150)}
                  </p>

                  <div className="card-footer">
                    <span>
                      {meeting.created_at
                        ? new Date(
                            meeting.created_at
                          ).toLocaleDateString()
                        : "Meeting"}
                    </span>

                    <button
                      className="text-button"
                      onClick={() =>
                        openMeeting(meetingId)
                      }
                    >
                      Open →
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </>
    );
  }

  /* ============================================================
     TASKS
  ============================================================ */

  function TasksPage() {
    return (
      <>
        <PageHeader
          title="Action Items"
          subtitle="Tasks extracted from your meetings"
        />

        <div className="panel">
          {loadingTasks ? (
            <Loading />
          ) : tasks.length === 0 ? (
            <EmptyState
              icon="✓"
              title="No action items"
              text="Tasks generated from your meetings will appear here."
            />
          ) : (
            <div className="full-task-list">
              {tasks.map((task, index) => {
                const completed =
                  getTaskStatus(task) ===
                  "completed";

                return (
                  <div
                    className="full-task-item"
                    key={
                      task.id ||
                      task.task_id ||
                      index
                    }
                  >
                    <button
                      className={`checkbox ${
                        completed
                          ? "checked"
                          : ""
                      }`}
                      onClick={() =>
                        toggleTask(task)
                      }
                    >
                      {completed ? "✓" : ""}
                    </button>

                    <div className="task-content">
                      <strong
                        className={
                          completed
                            ? "task-completed"
                            : ""
                        }
                      >
                        {getTaskTitle(task)}
                      </strong>

                      {task.description &&
                        task.description !==
                          getTaskTitle(task) && (
                          <p>
                            {task.description}
                          </p>
                        )}

                      <div className="task-meta">
                        <span
                          className={`status ${
                            completed
                              ? "status-completed"
                              : "status-pending"
                          }`}
                        >
                          {completed
                            ? "Completed"
                            : "Pending"}
                        </span>

                        {task.deadline && (
                          <span>
                            Due:{" "}
                            {new Date(
                              task.deadline
                            ).toLocaleDateString()}
                          </span>
                        )}

                        {task.due_date && (
                          <span>
                            Due:{" "}
                            {new Date(
                              task.due_date
                            ).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      className="delete-button"
                      onClick={() =>
                        deleteTask(
                          task.id ||
                            task.task_id
                        )
                      }
                    >
                      🗑
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </>
    );
  }

  /* ============================================================
     MEETING DETAILS
  ============================================================ */

  function MeetingDetails() {
    if (!selectedMeeting) return null;

    const transcript =
      selectedMeeting.transcript_text ||
      selectedMeeting.transcript;

    const summary =
      selectedMeeting.summary_text ||
      selectedMeeting.summary;

    return (
      <div className="meeting-details">
        <button
          className="back-button"
          onClick={() =>
            setSelectedMeeting(null)
          }
        >
          ← Back to meetings
        </button>

        <div className="panel">
          <div className="detail-icon">
            🎙️
          </div>

          <h1>
            {getMeetingTitle(selectedMeeting)}
          </h1>

          <p className="detail-description">
            {getMeetingDescription(
              selectedMeeting
            )}
          </p>

          <div className="detail-grid">
            <Detail
              label="Meeting ID"
              value={
                selectedMeeting.id ||
                selectedMeeting.meeting_id ||
                "—"
              }
            />

            <Detail
              label="Created"
              value={
                selectedMeeting.created_at
                  ? new Date(
                      selectedMeeting.created_at
                    ).toLocaleString()
                  : "—"
              }
            />

            <Detail
              label="Status"
              value={
                selectedMeeting.status ||
                "Available"
              }
            />
          </div>

          {transcript && (
            <div className="transcript">
              <h2>Transcript</h2>

              <div className="transcript-box">
                {transcript}
              </div>
            </div>
          )}

          {summary && (
            <div className="transcript">
              <h2>AI Summary</h2>

              <div className="transcript-box">
                {summary}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  /* ============================================================
     MAIN LAYOUT
  ============================================================ */

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            🤖
          </div>

          <div>
            <h2>Meeting AI</h2>
            <span>AI Meeting Agent</span>
          </div>
        </div>

        <nav className="nav">
          <button
            className={`nav-button ${
              activePage === "dashboard"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("dashboard")
            }
          >
            🏠 <span>Dashboard</span>
          </button>

          <button
            className={`nav-button ${
              activePage === "meetings"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("meetings")
            }
          >
            📊 <span>Meetings</span>
          </button>

          <button
            className={`nav-button ${
              activePage === "tasks"
                ? "active"
                : ""
            }`}
            onClick={() =>
              navigate("tasks")
            }
          >
            ✓ <span>Action Items</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button
            className="logout-button"
            onClick={logout}
          >
            ↪ <span>Logout</span>
          </button>
        </div>
      </aside>

      <main className="main">
        {error && (
          <div className="alert error">
            ⚠ {error}

            <button
              onClick={() => setError("")}
              className="alert-close"
            >
              ×
            </button>
          </div>
        )}

        {message && (
          <div className="alert success">
            ✓ {message}

            <button
              onClick={() => setMessage("")}
              className="alert-close"
            >
              ×
            </button>
          </div>
        )}

        {selectedMeeting ? (
          <MeetingDetails />
        ) : activePage === "dashboard" ? (
          <Dashboard />
        ) : activePage === "meetings" ? (
          <MeetingsPage />
        ) : (
          <TasksPage />
        )}
      </main>

      {/* ========================================================
          CREATE MEETING MODAL
      ======================================================== */}

      {showCreateMeeting && (
        <div
          className="modal-backdrop"
          onClick={() =>
            setShowCreateMeeting(false)
          }
        >
          <div
            className="modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >
            <h2>Create New Meeting</h2>

            <form onSubmit={createMeeting}>
              <div className="form-group">
                <label>Meeting Title</label>

                <input
                  type="text"
                  value={meetingTitle}
                  onChange={(e) =>
                    setMeetingTitle(
                      e.target.value
                    )
                  }
                  placeholder="e.g. Project Planning Meeting"
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowCreateMeeting(false)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                >
                  Create Meeting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================
          UPLOAD MEETING MODAL
      ======================================================== */}

      {showUploadMeeting && (
        <div
          className="modal-backdrop"
          onClick={() => {
            setShowUploadMeeting(false);
            setSelectedFile(null);
            setMeetingTitle("");
          }}
        >
          <div
            className="modal"
            onClick={(e) =>
              e.stopPropagation()
            }
          >
            <h2>Upload Meeting</h2>

            <form onSubmit={uploadMeeting}>
              <div className="form-group">
                <label>Meeting Title</label>

                <input
                  type="text"
                  value={meetingTitle}
                  onChange={(e) =>
                    setMeetingTitle(
                      e.target.value
                    )
                  }
                  placeholder="e.g. Weekly Team Meeting"
                />
              </div>

              <div className="form-group">
                <label>
                  Meeting Recording
                </label>

                <div className="file-input">
                  <input
                    type="file"
                    accept="audio/*,video/*"
                    onChange={(e) =>
                      setSelectedFile(
                        e.target.files?.[0] ||
                          null
                      )
                    }
                  />

                  {selectedFile && (
                    <p>
                      Selected:{" "}
                      <strong>
                        {selectedFile.name}
                      </strong>
                    </p>
                  )}
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setShowUploadMeeting(false);
                    setSelectedFile(null);
                    setMeetingTitle("");
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                >
                  Upload & Process
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   LOGIN SCREEN
============================================================ */

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [backendOnline, setBackendOnline] =
    useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/openapi.json`)
      .then((response) => {
        setBackendOnline(response.ok);
      })
      .catch(() => {
        setBackendOnline(false);
      });
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }

    if (!password) {
      setError("Password is required.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const token = await loginUser(
        email.trim(),
        password
      );

      onLogin(token);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          🤖
        </div>

        <h1>Meeting AI</h1>

        <p className="login-subtitle">
          AI-powered meeting intelligence
        </p>

        <div className="login-welcome">
          <h2>Welcome back</h2>

          <p>
            Sign in to access your meetings and
            action items.
          </p>
        </div>

        {backendOnline === false && (
          <div className="login-backend-warning">
            Cannot connect to the backend. Start
            FastAPI first.
          </div>
        )}

        {backendOnline === true && (
          <div className="login-backend-success">
            ✓ Backend connected
          </div>
        )}

        {error && (
          <div className="login-error">
            ⚠ {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="login-field">
            <label>Email</label>

            <input
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              placeholder="test@example.com"
              autoComplete="email"
              disabled={loading}
            />
          </div>

          <div className="login-field">
            <label>Password</label>

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>
        </form>

        <div className="login-security">
          🔒 Authentication secured by the FastAPI
          backend.
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   SMALL COMPONENTS
============================================================ */

function PageHeader({
  title,
  subtitle,
  actions,
}) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>

      {actions && (
        <div className="header-actions">
          {actions}
        </div>
      )}
    </div>
  );
}

function StatCard({
  icon,
  title,
  value,
  onClick,
}) {
  return (
    <div
      className="stat-card"
      onClick={onClick}
    >
      <div className="stat-icon">
        {icon}
      </div>

      <div className="stat-title">
        {title}
      </div>

      <div className="stat-value">
        {value}
      </div>
    </div>
  );
}

function Loading() {
  return (
    <div className="loading">
      <div className="spinner"></div>
      Loading...
    </div>
  );
}

function EmptyState({
  icon,
  title,
  text,
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        {icon}
      </div>

      <h3>{title}</h3>

      <p>{text}</p>
    </div>
  );
}

function Detail({
  label,
  value,
}) {
  return (
    <div className="detail-box">
      <span className="detail-label">
        {label}
      </span>

      <span className="detail-value">
        {value}
      </span>
    </div>
  );
}

export default App;