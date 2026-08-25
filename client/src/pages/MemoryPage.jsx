import React, { useEffect, useState } from "react";

const STORAGE_KEY = "meeting_ai_memories";

const defaultMemories = [
  {
    id: 1,
    title: "Project priorities",
    content: "Focus on improving meeting productivity and action tracking.",
    category: "Project",
    createdAt: new Date().toISOString(),
  },
  {
    id: 2,
    title: "Meeting preference",
    content: "Keep important decisions and action items easy to find.",
    category: "Preference",
    createdAt: new Date().toISOString(),
  },
];

function loadMemories() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // Ignore invalid storage.
  }

  return defaultMemories;
}

export default function MemoryPage() {
  const [memories, setMemories] = useState(loadMemories);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [showForm, setShowForm] = useState(false);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [newCategory, setNewCategory] = useState("General");

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(memories));
  }, [memories]);

  const filteredMemories = memories.filter((memory) => {
    const matchesSearch =
      memory.title.toLowerCase().includes(search.toLowerCase()) ||
      memory.content.toLowerCase().includes(search.toLowerCase());

    const matchesCategory =
      category === "All" || memory.category === category;

    return matchesSearch && matchesCategory;
  });

  function addMemory(event) {
    event.preventDefault();

    if (!title.trim() || !content.trim()) {
      return;
    }

    const memory = {
      id: Date.now(),
      title: title.trim(),
      content: content.trim(),
      category: newCategory,
      createdAt: new Date().toISOString(),
    };

    setMemories((current) => [memory, ...current]);

    setTitle("");
    setContent("");
    setNewCategory("General");
    setShowForm(false);
  }

  function deleteMemory(id) {
    setMemories((current) =>
      current.filter((memory) => memory.id !== id)
    );
  }

  function clearMemories() {
    if (!window.confirm("Delete all memories?")) {
      return;
    }

    setMemories([]);
  }

  const categories = [
    "All",
    ...new Set(memories.map((memory) => memory.category)),
  ];

  return (
    <>
      <div className="page-header">
        <div>
          <h1>MCP Memory</h1>
          <p>Manage information available to your AI assistant</p>
        </div>

        <div className="header-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={clearMemories}
          >
            Clear All
          </button>

          <button
            type="button"
            className="primary-button"
            onClick={() => setShowForm((value) => !value)}
          >
            + Add Memory
          </button>
        </div>
      </div>

      {showForm && (
        <section className="panel memory-form-panel">
          <h2>Add Memory</h2>

          <form onSubmit={addMemory}>
            <div className="form-group">
              <label htmlFor="memory-title">Title</label>

              <input
                id="memory-title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="e.g. Project deadline"
              />
            </div>

            <div className="form-group">
              <label htmlFor="memory-category">Category</label>

              <select
                id="memory-category"
                value={newCategory}
                onChange={(event) => setNewCategory(event.target.value)}
              >
                <option>General</option>
                <option>Project</option>
                <option>Preference</option>
                <option>Meeting</option>
                <option>Important</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="memory-content">Memory</label>

              <textarea
                id="memory-content"
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="Enter information you want the assistant to remember..."
                rows="4"
              />
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>

              <button type="submit" className="primary-button">
                Save Memory
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="memory-toolbar">
          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search memories..."
          />

          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            {categories.map((item) => (
              <option key={item}>{item}</option>
            ))}
          </select>
        </div>

        {filteredMemories.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🧠</div>
            <h3>No memories found</h3>
            <p>Add a memory or change your search.</p>
          </div>
        ) : (
          <div className="memory-list">
            {filteredMemories.map((memory) => (
              <article className="memory-card" key={memory.id}>
                <div className="memory-card-header">
                  <div>
                    <h3>{memory.title}</h3>
                    <span className="memory-category">
                      {memory.category}
                    </span>
                  </div>

                  <button
                    type="button"
                    className="delete-button"
                    onClick={() => deleteMemory(memory.id)}
                  >
                    🗑
                  </button>
                </div>

                <p>{memory.content}</p>

                <small>
                  Created{" "}
                  {new Date(memory.createdAt).toLocaleDateString()}
                </small>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}