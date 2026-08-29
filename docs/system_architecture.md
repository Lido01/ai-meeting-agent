
# 1. System Architecture Flow
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


# 2. Important Frontend Rules

The frontend must NOT:

- Connect directly to PostgreSQL.
- Call Gemini directly.
- Send passwords to PostgreSQL.
- Send user_id manually for protected APIs.
- Store the JWT in normal application state only.

The frontend SHOULD:

- Communicate through FastAPI.
- Send JWT with protected requests.
- Send uploaded files to FastAPI.
- Display loading states.
- Display API errors.
- Redirect to login when authentication fails.


---

# 3. Backend Responsibilities

The frontend only sends requests.

FastAPI is responsible for:

- Authentication
- JWT verification
- File upload
- Audio processing
- Gemini transcription
- MCP context
- AI analysis
- Summary generation
- Action item extraction
- Deadline parsing
- Task creation
- PostgreSQL storage
- Task CRUD
- User data isolation


---

# 4. Main MVP Goal

The complete user experience should be:
User registers
      ↓
User logs in
      ↓
JWT token
      ↓
Dashboard
      ↓
Upload meeting
      ↓
AI processes meeting
      ↓
Summary generated
      ↓
Action items extracted
      ↓
Tasks created
      ↓
User views tasks
      ↓
User completes/updates tasks

This is the main AI Meeting Agent MVP.



# 5. Flow After COntext Continuity Added


                UPLOAD AUDIO
                     │
                     ▼
                TRANSCRIPTION
                     │
                     ▼
             GET PREVIOUS CONTEXT
                     │
                     ▼
              AI MEETING AGENT
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       SUMMARY              ACTION ITEMS
          │                     │
          │                     ▼
          │                CREATE TASKS
          │
          ▼
   CONTEXT CONTINUITY
       ANALYSIS
          │
          ▼
    Was something
       changed?
          │
      ┌───┴────┐
      │        │
     NO       YES
      │        │
      ▼        ▼
   Nothing   Save as
             PENDING
                │
                ▼
       Frontend shows:
       "Confirm update?"
                │
          ┌─────┴─────┐
          ▼           ▼
       Confirm       Reject
          │           │
          ▼           ▼
    Update task    Keep old task
