import React, { useEffect, useState } from "react";

const STORAGE_KEY = "meeting_ai_chat_history";

const suggestedPrompts = [
  "Summarize my recent meetings",
  "What are my pending action items?",
  "What decisions were made recently?",
  "Show me meetings that need follow-up",
];

function getInitialMessages() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // Ignore invalid local storage data.
  }

  return [
    {
      id: 1,
      role: "assistant",
      text: "Hello! I'm your AI Meeting Assistant. Ask me about your meetings, action items, decisions, or follow-ups.",
    },
  ];
}

function generateFrontendResponse(message) {
  const text = message.toLowerCase();

  if (text.includes("pending") || text.includes("task")) {
    return "I can help you review your action items. Connect the task backend later and I can provide real-time task summaries here.";
  }

  if (text.includes("summar")) {
    return "I can summarize your meetings once meeting data is connected. For now, this assistant interface is running entirely on the frontend.";
  }

  if (text.includes("decision")) {
    return "I can identify important decisions from meeting transcripts once the meeting and AI-processing APIs are connected.";
  }

  if (text.includes("follow")) {
    return "I can help identify follow-ups from your meetings. The frontend is ready for the backend integration.";
  }

  return `I received: "${message}". The AI Assistant UI is working. Connect your AI endpoint later to replace this frontend response with a real AI response.`;
}

export default function AssistantPage() {
  const [messages, setMessages] = useState(getInitialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  async function handleSend(event) {
    event.preventDefault();

    const text = input.trim();

    if (!text || loading) {
      return;
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      text,
    };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setLoading(true);

    setTimeout(() => {
      const response = {
        id: Date.now() + 1,
        role: "assistant",
        text: generateFrontendResponse(text),
      };

      setMessages((current) => [...current, response]);
      setLoading(false);
    }, 700);
  }

  function handlePrompt(prompt) {
    setInput(prompt);
  }

  function clearChat() {
    const initialMessage = {
      id: Date.now(),
      role: "assistant",
      text: "New conversation started. How can I help?",
    };

    setMessages([initialMessage]);
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1>AI Assistant</h1>
          <p>Your intelligent meeting workspace</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={clearChat}
        >
          Clear Chat
        </button>
      </div>

      <div className="assistant-layout">
        <section className="panel assistant-panel">
          <div className="assistant-header">
            <div className="assistant-avatar">🤖</div>

            <div>
              <h2>Meeting AI</h2>
              <span className="online-status">● Ready</span>
            </div>
          </div>

          <div className="chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${
                  message.role === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
              >
                <div className="message-avatar">
                  {message.role === "user" ? "👤" : "🤖"}
                </div>

                <div className="message-content">
                  {message.text}
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-message assistant-message">
                <div className="message-avatar">🤖</div>

                <div className="message-content typing">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          <form className="chat-input-area" onSubmit={handleSend}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about your meetings..."
              disabled={loading}
            />

            <button
              type="submit"
              className="primary-button"
              disabled={!input.trim() || loading}
            >
              Send
            </button>
          </form>
        </section>

        <aside className="panel suggestions-panel">
          <h2>Suggested Prompts</h2>
          <p>Try asking the assistant:</p>

          <div className="suggestion-list">
            {suggestedPrompts.map((prompt) => (
              <button
                type="button"
                key={prompt}
                className="suggestion-button"
                onClick={() => handlePrompt(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="assistant-info">
            <strong>Frontend mode</strong>
            <p>
              The assistant interface is currently operating without a
              backend AI endpoint.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}