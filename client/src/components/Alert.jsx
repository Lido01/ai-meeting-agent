import React from "react";
export default function Alert({ type, children, onClose }) {
  return (
    <div className={`alert ${type}`}>
      {type === "error" ? "⚠" : "✓"} {children}
      <button onClick={onClose} className="alert-close">
        ×
      </button>
    </div>
  );
}
