import React, { useEffect, useState } from "react";

const STORAGE_KEY = "meeting_ai_integrations";

const integrations = [
  {
    id: "google-calendar",
    name: "Google Calendar",
    icon: "📅",
    description: "Sync meetings and calendar events.",
  },
  {
    id: "slack",
    name: "Slack",
    icon: "💬",
    description: "Send meeting summaries and action items to Slack.",
  },
  {
    id: "google-drive",
    name: "Google Drive",
    icon: "📁",
    description: "Store meeting recordings and generated documents.",
  },
  {
    id: "notion",
    name: "Notion",
    icon: "📝",
    description: "Save meeting notes and action items to Notion.",
  },
  {
    id: "mcp",
    name: "MCP Server",
    icon: "🧠",
    description: "Connect external tools and memory providers.",
  },
];

function loadConnections() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // Ignore invalid storage.
  }

  return {};
}

export default function IntegrationsPage() {
  const [connections, setConnections] = useState(loadConnections);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(connections));
  }, [connections]);

  function toggleIntegration(id) {
    setConnections((current) => ({
      ...current,
      [id]: !current[id],
    }));
  }

  const connectedCount = integrations.filter(
    (integration) => connections[integration.id]
  ).length;

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Integrations</h1>
          <p>Connect Meeting AI with your favorite tools</p>
        </div>
      </div>

      <section className="panel integration-summary">
        <div>
          <span>Connected integrations</span>
          <strong>{connectedCount}</strong>
        </div>

        <div>
          <span>Available integrations</span>
          <strong>{integrations.length}</strong>
        </div>
      </section>

      <div className="integration-grid">
        {integrations.map((integration) => {
          const connected = Boolean(connections[integration.id]);

          return (
            <article className="panel integration-card" key={integration.id}>
              <div className="integration-icon">
                {integration.icon}
              </div>

              <div className="integration-content">
                <div className="integration-title">
                  <h2>{integration.name}</h2>

                  <span
                    className={
                      connected
                        ? "integration-connected"
                        : "integration-disconnected"
                    }
                  >
                    {connected ? "Connected" : "Not connected"}
                  </span>
                </div>

                <p>{integration.description}</p>

                <button
                  type="button"
                  className={
                    connected
                      ? "secondary-button"
                      : "primary-button"
                  }
                  onClick={() => toggleIntegration(integration.id)}
                >
                  {connected ? "Disconnect" : "Connect"}
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </>
  );
}