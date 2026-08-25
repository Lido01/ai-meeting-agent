import React, { useEffect, useState } from "react";

const STORAGE_KEY = "meeting_ai_team";

const defaultMembers = [
  {
    id: 1,
    name: "RK",
    email: "rk@example.com",
    role: "Owner",
    status: "Active",
  },
];

function loadMembers() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved) {
      return JSON.parse(saved);
    }
  } catch {
    // Ignore invalid storage.
  }

  return defaultMembers;
}

export default function TeamPage() {
  const [members, setMembers] = useState(loadMembers);
  const [showInvite, setShowInvite] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("Member");

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(members));
  }, [members]);

  function inviteMember(event) {
    event.preventDefault();

    if (!name.trim() || !email.trim()) {
      return;
    }

    const member = {
      id: Date.now(),
      name: name.trim(),
      email: email.trim(),
      role,
      status: "Invited",
    };

    setMembers((current) => [...current, member]);

    setName("");
    setEmail("");
    setRole("Member");
    setShowInvite(false);
  }

  function removeMember(id) {
    if (!window.confirm("Remove this team member?")) {
      return;
    }

    setMembers((current) =>
      current.filter((member) => member.id !== id)
    );
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Team</h1>
          <p>Manage your Meeting AI workspace members</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setShowInvite((value) => !value)}
        >
          + Invite Member
        </button>
      </div>

      {showInvite && (
        <section className="panel">
          <h2>Invite Team Member</h2>

          <form onSubmit={inviteMember}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="team-name">Name</label>

                <input
                  id="team-name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="John Doe"
                />
              </div>

              <div className="form-group">
                <label htmlFor="team-email">Email</label>

                <input
                  id="team-email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="john@example.com"
                />
              </div>

              <div className="form-group">
                <label htmlFor="team-role">Role</label>

                <select
                  id="team-role"
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                >
                  <option>Member</option>
                  <option>Admin</option>
                  <option>Viewer</option>
                </select>
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowInvite(false)}
              >
                Cancel
              </button>

              <button type="submit" className="primary-button">
                Send Invitation
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Team Members</h2>
            <p>{members.length} member(s) in this workspace</p>
          </div>
        </div>

        <div className="team-list">
          {members.map((member) => (
            <div className="team-member" key={member.id}>
              <div className="member-avatar">
                {member.name.charAt(0).toUpperCase()}
              </div>

              <div className="member-info">
                <strong>{member.name}</strong>
                <span>{member.email}</span>
              </div>

              <span className="member-role">{member.role}</span>

              <span
                className={`member-status ${
                  member.status === "Active"
                    ? "active"
                    : "invited"
                }`}
              >
                {member.status}
              </span>

              {member.role !== "Owner" && (
                <button
                  type="button"
                  className="delete-button"
                  onClick={() => removeMember(member.id)}
                >
                  🗑
                </button>
              )}
            </div>
          ))}
        </div>
      </section>
    </>
  );
}