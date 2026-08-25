import React, { useEffect, useState } from "react";

const STORAGE_KEY = "meeting_ai_settings";

const defaultSettings = {
  notifications: true,
  taskNotifications: true,
  meetingNotifications: true,
  autoSummary: true,
  autoTasks: true,
  contextAlerts: true,
};

function loadSettings() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return {
        ...defaultSettings,
        ...JSON.parse(saved),
      };
    }
  } catch {
    // Ignore invalid local storage data.
  }

  return defaultSettings;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState(loadSettings);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  function updateSetting(key, value) {
    setSettings((current) => ({
      ...current,
      [key]: value,
    }));

    setSaved(false);
  }

  function handleSave() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));

    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 2000);
  }

  function resetSettings() {
    const confirmed = window.confirm(
      "Reset all Meeting AI settings to their defaults?"
    );

    if (!confirmed) {
      return;
    }

    setSettings(defaultSettings);
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(defaultSettings)
    );

    setSaved(false);
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Manage your Meeting AI preferences</p>
        </div>
      </div>

      <div className="settings-page">
        {/* Notifications */}
        <section className="panel settings-section">
          <div className="settings-heading">
            <h2>Notifications</h2>
            <p>Choose which Meeting AI notifications you receive.</p>
          </div>

          <label className="setting-toggle">
            <span>
              <strong>All notifications</strong>
              <small>
                Enable or disable application notifications.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.notifications}
              onChange={(event) =>
                updateSetting(
                  "notifications",
                  event.target.checked
                )
              }
            />
          </label>

          <label className="setting-toggle">
            <span>
              <strong>Meeting notifications</strong>
              <small>
                Notify me about meeting activity.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.meetingNotifications}
              disabled={!settings.notifications}
              onChange={(event) =>
                updateSetting(
                  "meetingNotifications",
                  event.target.checked
                )
              }
            />
          </label>

          <label className="setting-toggle">
            <span>
              <strong>Task notifications</strong>
              <small>
                Notify me when action items change.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.taskNotifications}
              disabled={!settings.notifications}
              onChange={(event) =>
                updateSetting(
                  "taskNotifications",
                  event.target.checked
                )
              }
            />
          </label>
        </section>

        {/* AI Features */}
        <section className="panel settings-section">
          <div className="settings-heading">
            <h2>AI Features</h2>
            <p>Control automatic Meeting AI features.</p>
          </div>

          <label className="setting-toggle">
            <span>
              <strong>Automatic summaries</strong>
              <small>
                Generate meeting summaries automatically.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.autoSummary}
              onChange={(event) =>
                updateSetting(
                  "autoSummary",
                  event.target.checked
                )
              }
            />
          </label>

          <label className="setting-toggle">
            <span>
              <strong>Automatic action items</strong>
              <small>
                Extract action items from meetings automatically.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.autoTasks}
              onChange={(event) =>
                updateSetting(
                  "autoTasks",
                  event.target.checked
                )
              }
            />
          </label>

          <label className="setting-toggle">
            <span>
              <strong>Context Continuity Alerts</strong>
              <small>
                Warn me when a deadline, owner, or decision
                changes between meetings.
              </small>
            </span>

            <input
              type="checkbox"
              checked={settings.contextAlerts}
              onChange={(event) =>
                updateSetting(
                  "contextAlerts",
                  event.target.checked
                )
              }
            />
          </label>
        </section>

        {/* Storage */}
        <section className="panel settings-section">
          <div className="settings-heading">
            <h2>Local Settings</h2>
            <p>
              Your preferences are stored locally in this browser.
            </p>
          </div>

          <div className="settings-local-info">
            <span className="settings-local-icon">💾</span>

            <div>
              <strong>Browser storage</strong>
              <p>
                No backend connection is required for these
                preferences.
              </p>
            </div>
          </div>
        </section>

        {/* Actions */}
        <div className="settings-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={resetSettings}
          >
            Reset Defaults
          </button>

          <button
            type="button"
            className="primary-button"
            onClick={handleSave}
          >
            Save Settings
          </button>

          {saved && (
            <span className="save-message">
              ✓ Settings saved
            </span>
          )}
        </div>
      </div>
    </>
  );
}