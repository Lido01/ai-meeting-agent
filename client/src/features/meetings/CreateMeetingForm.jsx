import React, { useState } from "react";

export default function CreateMeetingForm({
  onSubmit,
  onCancel,
  loading = false,
}) {
  const [title, setTitle] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (!title.trim()) {
      return onSubmit(null, "Meeting title is required.");
    }

    onSubmit(title.trim());
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="meeting-title">Meeting Title</label>

        <input
          id="meeting-title"
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="e.g. Project Planning Meeting"
          disabled={loading}
          autoFocus
        />
      </div>

      <div className="modal-actions">
        <button
          type="button"
          className="secondary-button"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </button>

        <button
          type="submit"
          className="primary-button"
          disabled={loading}
        >
          {loading ? "Creating..." : "Create Meeting"}
        </button>
      </div>
    </form>
  );
}