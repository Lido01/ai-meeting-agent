import React, { useState } from "react";

export default function AudioUploader({
  onSubmit,
  onCancel,
  loading = false,
}) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  function handleSubmit(event) {
    event.preventDefault();

    if (!selectedFile) {
      return onSubmit(
        null,
        null,
        "Please select an audio or video file."
      );
    }

    if (!title.trim()) {
      return onSubmit(
        null,
        null,
        "Meeting title is required."
      );
    }

    onSubmit(title.trim(), selectedFile);
  }

  function handleDrop(event) {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];

    if (file) {
      setSelectedFile(file);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="meeting-title">
          Meeting Title
        </label>

        <input
          id="meeting-title"
          type="text"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="e.g. Weekly Team Meeting"
          disabled={loading}
        />
      </div>

      <div className="form-group">
        <label htmlFor="meeting-recording">
          Meeting Recording
        </label>

        <div
          className="file-input"
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          <input
            id="meeting-recording"
            type="file"
            accept="audio/*,video/*"
            onChange={(event) =>
              setSelectedFile(
                event.target.files?.[0] || null
              )
            }
            disabled={loading}
          />

          {selectedFile && (
            <p>
              Selected:{" "}
              <strong>{selectedFile.name}</strong>
            </p>
          )}
        </div>
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
          {loading
            ? "Uploading & Processing..."
            : "Upload & Process"}
        </button>
      </div>
    </form>
  );
}