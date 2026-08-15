# AI Meeting Agent - Frontend Client

An AI-powered dashboard that allows teams to upload meeting audio or transcripts, view AI-generated summaries, track extracted action items, and manage team task assignments in real-time.

---

## 🎯 Project Overview

The **AI Meeting Agent Frontend** is a modern web application built for remote teams and project managers. It serves as the visual control center for the AI Meeting Agent ecosystem, providing an intuitive interface to:

- Upload raw meeting audio (`.mp3`, `.wav`) or plain text transcripts.
- View real-time processing status and AI-generated meeting summaries.
- Track structured action items, assignees, deadlines, and task completion states.
- Review historical meeting contexts and past decisions.

---

## ⚡ Tech Stack

- **Framework:** [React 18](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Icons:** [Lucide React](https://lucide.dev/)
- **HTTP Client:** [Axios](https://axios-http.com/)
- **Routing:** [React Router v6](https://reactrouter.com/)

---

## 🔄 System Flow & How It Works

┌─────────────────────────┐
│     User Uploads        │
│ Audio (.mp3) / Text     │
└───────────┬─────────────┘
│
▼
┌─────────────────────────┐
│     FastAPI Backend     │
│   Processing Pipeline   │
└───────────┬─────────────┘
│
├──► 1. Transcribe Audio (Gemini API)
├──► 2. Query Historical Memory (MCP)
├──► 3. Summarize & Extract Tasks (Gemini API)
└──► 4. Persist Data (PostgreSQL)
│
▼
┌─────────────────────────┐
│   React Dashboard UI    │
│ Displays Summary/Tasks  │
└─────────────────────────┘

1. **Ingestion:** The user submits a meeting title along with an audio recording or text transcript via the dashboard upload interface.
2. **Backend Processing:** The frontend dispatches an API call to the Python FastAPI backend.
3. **AI Pipeline:** The backend coordinates with Google Gemini for transcription/analysis and MCP for historical context retrieval.
4. **Data Visualization:** Structured JSON responses return to the frontend, instantly populating meeting summaries, action items, assignees, and deadlines.

---

## 📁 Folder Structure

```text
client/
├── public/                  # Static assets (favicons, public images)
├── src/
│   ├── assets/              # SVGs, logos, and global static media
│   ├── components/          # Reusable UI components
│   │   ├── common/          # Buttons, Modals, Loaders, Inputs
│   │   ├── layout/          # Navbar, Sidebar, Footer
│   │   └── meetings/        # MeetingCard, UploadModal, TaskList
│   ├── context/             # React Context for global state (Auth, Theme)
│   ├── hooks/               # Custom React hooks (e.g., useMeetings, useTasks)
│   ├── pages/               # Top-level view routes
│   │   ├── Dashboard.jsx     # Main overview page
│   │   ├── MeetingDetails.jsx# Detailed meeting view with summary & tasks
│   │   ├── Tasks.jsx        # Kanban / List view of all assigned tasks
│   │   └── NotFound.jsx     # 404 page
│   ├── services/            # API integration modules
│   │   ├── api.js           # Axios instance configuration
│   │   └── meetingService.js# API methods for meetings & tasks
│   ├── utils/               # Helper functions, date formatters, validators
│   ├── App.jsx              # Main App wrapper & route setup
│   ├── index.css            # Tailwind directives and global styles
│   └── main.jsx             # React entry point
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore configuration
├── index.html               # Vite HTML template
├── package.json             # Dependencies and scripts
├── postcss.config.js        # PostCSS configuration for Tailwind
├── tailwind.config.js       # Tailwind CSS configuration
└── vite.config.js           # Vite build configuration

