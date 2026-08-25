import React from "react";

export default function StatCard({ icon, title, value, onClick }) {
  return (
    <div className="stat-card" onClick={onClick}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}