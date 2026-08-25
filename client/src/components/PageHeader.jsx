import React from "react";

export default function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>

      {actions && <div className="header-actions">{actions}</div>}
    </div>
  );
}