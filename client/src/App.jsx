
import React, { useCallback, useState } from "react";
import { useAuth } from "./context/AuthContext";

import Sidebar from "./components/Sidebar";
import Alert from "./components/Alert";

import Login from "./features/auth/Login";

import Dashboard from "./pages/Dashboard";
import MeetingsPage from "./pages/MeetingsPage";
import TasksPage from "./pages/TasksPage";
import AIAssistantPage from "./pages/AIAssistantPage";
import MemoryPage from "./pages/MemoryPage";
import TeamPage from "./pages/TeamPage";
import IntegrationsPage from "./pages/IntegrationsPage";
import ContextAlertsPage from "./pages/ContextAlertsPage";
import SettingsPage from "./pages/SettingsPage";

import MeetingDetails from "./features/meetings/MeetingDetails";

export default function App() {
  const { isAuthenticated, logout } = useAuth();

  const [activePage, setActivePage] = useState("dashboard");
  const [selectedMeeting, setSelectedMeeting] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const handleNavigate = useCallback((page) => {
    setActivePage(page);
    setSelectedMeeting(null);
    setError("");
    setMessage("");
  }, []);

  const handleOpenMeeting = useCallback((meeting) => {
    setSelectedMeeting(meeting);
    setError("");
    setMessage("");
  }, []);

  const handleDataChanged = useCallback(() => {
    setRefreshKey((value) => value + 1);
  }, []);

  const handleLogout = useCallback(() => {
    logout();

    setActivePage("dashboard");
    setSelectedMeeting(null);
    setError("");
    setMessage("");
  }, [logout]);

  if (!isAuthenticated) {
    return <Login />;
  }

  function renderPage() {
    if (selectedMeeting) {
      return (
        <MeetingDetails
          meeting={selectedMeeting}
          onBack={() => setSelectedMeeting(null)}
        />
      );
    }

    switch (activePage) {
      case "dashboard":
        return (
          <Dashboard
            onNavigate={handleNavigate}
            onOpenMeeting={handleOpenMeeting}
            refreshKey={refreshKey}
            onError={setError}
          />
        );

      case "meetings":
        return (
          <MeetingsPage
            onOpenMeeting={handleOpenMeeting}
            refreshKey={refreshKey}
            onDataChanged={handleDataChanged}
          />
        );

      case "tasks":
        return (
          <TasksPage
            refreshKey={refreshKey}
            onDataChanged={handleDataChanged}
          />
        );

      case "assistant":
        return <AIAssistantPage />;

      case "memory":
        return <MemoryPage />;

      case "team":
        return <TeamPage />;

      case "integrations":
        return <IntegrationsPage />;

      case "context-alerts":
        return (
          <ContextAlertsPage
            refreshKey={refreshKey}
            onDataChanged={handleDataChanged}
          />
        );

      case "settings":
        return <SettingsPage />;

      default:
        return (
          <Dashboard
            onNavigate={handleNavigate}
            onOpenMeeting={handleOpenMeeting}
            refreshKey={refreshKey}
            onError={setError}
          />
        );
    }
  }

  return (
    <div className="app">
      <Sidebar
        activePage={activePage}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
      />

      <main className="main">
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

        {renderPage()}
      </main>
    </div>
  );
}

