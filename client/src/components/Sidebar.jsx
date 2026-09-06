import React from "react";

export default function Sidebar({ activePage, onNavigate, onLogout }) {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="brand">
        <div className="brand-icon">🤖</div>

        <div>
          <h2>Meeting AI</h2>
          <span>AI Meeting Agent</span>
        </div>
      </div>

      <nav className="nav">
        {/* WORKSPACE */}
        <div className="nav-section">
          <div className="nav-section-title">WORKSPACE</div>

          <button
            type="button"
            className={
              activePage === "dashboard"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("dashboard")}
          >
             <span>Dashboard</span>
          </button>

          <button
            type="button"
            className={
              activePage === "meetings"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("meetings")}
          >
             <span>Meetings</span>
          </button>

          <button
            type="button"
            className={
              activePage === "tasks"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("tasks")}
          >
            ✓ <span>Action Items</span>
          </button>
        </div>

        {/* AI & INTELLIGENCE */}
        <div className="nav-section">
          <div className="nav-section-title">AI & INTELLIGENCE</div>

          <button
            type="button"
            className={
              activePage === "assistant"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("assistant")}
          >
             <span>AI Assistant</span>
          </button>

          <button
            type="button"
            className={
              activePage === "memory"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("memory")}
          >
            <span>MCP Memory</span>
          </button>

          <button
            type="button"
            className={
              activePage === "context-alerts"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("context-alerts")}
          >
             <span>Context Alerts</span>
          </button>
        </div>

        {/* ORGANIZATION */}
        <div className="nav-section">
          <div className="nav-section-title">ORGANIZATION</div>

          <button
            type="button"
            className={
              activePage === "team"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("team")}
          >
             <span>Team</span>
          </button>

          <button
            type="button"
            className={
              activePage === "integrations"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("integrations")}
          >
             <span>Integrations</span>
          </button>

          <button
            type="button"
            className={
              activePage === "settings"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => onNavigate("settings")}
          >
            <span>Settings</span>
          </button>
        </div>
      </nav>

      {/* Logout */}
      <div className="sidebar-bottom">
        <button
          type="button"
          className="logout-button"
          onClick={onLogout}
        >
          ↪ <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
