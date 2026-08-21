# AI Meeting Agent

AI-powered meeting assistant that processes recorded meetings, generates transcripts and summaries, and extracts actionable tasks with assignees and deadlines.

The project is designed to help remote teams and managers automatically understand meeting discussions and track follow-up tasks.

---

## 🚀 Project Overview

The AI Meeting Agent allows users to upload a recorded meeting or meeting transcript.

The backend processes the meeting using Google Gemini and stores the results in PostgreSQL.

The planned system will:

- Upload meeting recordings or text transcripts
- Transcribe meeting audio using Google Gemini
- Generate meeting summaries
- Identify important topics
- Extract action items
- Identify task assignees
- Identify deadlines
- Store meetings and tasks in PostgreSQL
- Use MCP (Model Context Protocol) to retrieve context from previous meetings
- Provide APIs for a future frontend dashboard
- Monitor system performance using observability tools

---

## 🏗️ System Architecture

```text
                    AI Meeting Agent
                           |
                           v
                  +------------------+
                  |     Frontend     |
                  |   React / Vite   |
                  +--------+---------+
                           |
                           | HTTP API
                           v
                  +------------------+
                  |     FastAPI      |
                  |     Backend      |
                  +--------+---------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
      +------------+ +-----------+ +-----------+
      | PostgreSQL | |   Gemini  | |    MCP    |
      |  Database  | |    API    | |   Server  |
      +------------+ +-----------+ +-----------+
             |             |             |
             |             v             |
             |       Transcript /       |
             |       Summary / Tasks    |
             |             |             |
             +-------------+-------------+
                           |
                           v
                     Meeting Results

```

## Folder Strucure

meeting-agent/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── meetings.py
│   │   │   ├── tasks.py
│   │   │   └── users.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── meeting.py
│   │   │   └── task.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── meeting.py
│   │   │   └── task.py
│   │   │
│   │   ├── services/
│   │   │   ├── meeting_service.py
│   │   │   ├── gemini_service.py
│   │   │   ├── transcription_service.py
│   │   │   └── task_extraction_service.py
│   │   │
│   │   └── mcp/
│   │       └── server.py
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   └── ...
│
├── docker-compose.yml
│
└── README.md