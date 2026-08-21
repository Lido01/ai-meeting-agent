                 ┌──────────────────────┐
                 │    Current Meeting   │
                 └──────────┬───────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    Gemini   │
                     │    Agent    │
                     └──────┬──────┘
                            │
                  "I need historical
                    context."
                            │
                            ▼
                     ┌─────────────┐
                     │ MCP Tool    │
                     │             │
                     │ search_     │
                     │ meetings()  │
                     └──────┬──────┘
                            │
                            ▼
                       PostgreSQL
                            │
                            ▼
                     Previous Context
                            │
                            ▼
                     ┌─────────────┐
                     │    Gemini   │
                     └──────┬──────┘
                            │
                            ▼
                     Extract Tasks
                            │
                            ▼
                       PostgreSQL


STEP 1 → Create GitHub repo
STEP 2 → Create FastAPI project
STEP 3 → Install PostgreSQL
STEP 4 → Connect FastAPI → PostgreSQL
STEP 5 → Create database models
STEP 6 → Create API endpoints
STEP 7 → Add authentication
STEP 8 → Add meeting upload
STEP 9 → Connect Gemini
STEP 10 → Add MCP
STEP 11 → Test complete AI pipeline
STEP 12 → Backend finished
                    ↓
              THEN frontend



<!-- file .mp, m4a, .txt file accept flow -->
User
 ↓
Upload meeting.mp3
 ↓
FastAPI
 ↓
Save file
 ↓
Create Meeting record
 ↓
Gemini
 ↓
Transcript
 ↓
Summary
 ↓
Action Items
 ↓
Tasks

# 🚧 Development Roadmap
## Phase 1 — Backend Foundation
      FastAPI setup
      PostgreSQL setup
      SQLAlchemy setup
      Alembic migrations
      User model
      Meeting model
      Task model
      User API
      Meeting API
      Task API

## Phase 2 — Meeting Processing
      Meeting file upload
      Gemini API connection
      Audio transcription --- ?
      Meeting summary
      Topic extraction 
      Action-item extraction
      Assignee extraction
      Deadline extraction
      Automatic task creation

## Phase 3 — AI Agent + MCP
      MCP server
      Search previous meetings
      Retrieve previous tasks
      Retrieve team members
      Historical context analysis
      Agent-based task updates

## Phase 4 — Frontend
      React setup
      Login/register
      Meeting upload page
      Meeting list
      Meeting details
      Summary display
      Task dashboard
      Task status management

## Phase 5 — Observability
      Prometheus
      Grafana
      Processing-time metrics
      AI request metrics
      Error monitoring
      Task extraction metrics