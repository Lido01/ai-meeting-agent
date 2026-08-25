import React from "react";
export default function Detail({ label, value }) {
  return (
    <div className="detail-box">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value}</span>
    </div>
  );
}
