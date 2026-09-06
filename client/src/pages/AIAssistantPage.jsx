import React, { useEffect, useState } from "react";
import { getDemoMeetingMemoryReply } from "../data/demoMeetingMemory";
import { sendAssistantMessage } from "../services/assistantService";

const STORAGE_KEY = "meeting_ai_chat_history";

const suggestedPrompts = [
  "What was decided about the authentication task?",
  "Who is responsible for it now?",
  "What changed between the meetings?",
  "Summarize my recent meetings",
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

    try {
      const demoReply = getDemoMeetingMemoryReply(text);

      if (demoReply) {
        setMessages((current) => [
          ...current,
          {
            id: Date.now() + 1,
            role: "assistant",
            text: demoReply.reply,
            contextLabel: demoReply.contextLabel,
          },
        ]);
        return;
      }

      const reply = await sendAssistantMessage(text);

      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: reply,
          contextLabel: "🧠 Retrieved from meeting memory",
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          text:
            error?.message ||
            "I couldn't retrieve your previous meeting context right now. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
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

                  {message.contextLabel && (
                    <span className="message-context-source">
                      {message.contextLabel}
                    </span>
                  )}
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
            <strong>Meeting context</strong>
            <p>
              Ask about previous meetings, assignees, and deadlines.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}