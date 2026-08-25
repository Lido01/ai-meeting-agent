# AI Meeting Agent — API Endpoints

## 1. Overview

The AI Meeting Agent frontend communicates with the FastAPI backend.

The frontend must NEVER connect directly to PostgreSQL.

Architecture:

Frontend
   ↓
FastAPI Backend
   ↓
PostgreSQL
   ↓
Gemini + MCP
   ↓
FastAPI
   ↓
Frontend


Main frontend flow:

Login
   ↓
Receive JWT token
   ↓
Upload meeting
   ↓
Gemini transcribes meeting
   ↓
MCP gets previous meeting context
   ↓
AI Agent analyzes current + previous context
   ↓
Summary + action items created
   ↓
Tasks saved
   ↓
Context changes detected
   ↓
Frontend displays Context Continuity Alert
   ↓
User clicks Confirm or Reject
   ↓
If Confirm → task is updated
   ↓
Frontend refreshes task list


---

# 2. Backend Base URL

For local development:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs


The frontend should use:

const API_BASE_URL = "http://127.0.0.1:8000";


Do NOT connect the frontend directly to PostgreSQL.


---

# 3. Authentication

The application uses JWT authentication.

The frontend must:

1. Register a user.
2. Login.
3. Receive the JWT access token.
4. Store the access token.
5. Send the token with protected API requests.


Protected requests use:

Authorization: Bearer ACCESS_TOKEN


Example:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...


IMPORTANT:

The frontend should NOT manually send:

user_id=1


The backend gets the logged-in user's ID from the JWT token for protected endpoints.


---

# 4. User Registration

## Endpoint

POST /users/

## Authentication

Not required.

## Purpose

Create a new user account.


## Request

Content-Type:

application/json


Example:

{
  "name": "John",
  "email": "john@example.com",
  "password": "Test1234!",
  "role": "user"
}


## Fields

| Field | Type | Required | Description |
|---|---|---|---|
| name | string | Yes | User's name |
| email | string | Yes | User's email |
| password | string | Yes | User's password |
| role | string | No | User role |


## Response

Example:

{
  "id": 1,
  "name": "John",
  "email": "john@example.com",
  "role": "user"
}


IMPORTANT:

The backend does NOT return the password.

The backend stores a hashed password.


---

# 5. Login

## Endpoint

POST /auth/login

## Authentication

Not required.

## Purpose

Login a user and receive a JWT access token.


## Request

This endpoint uses form data.

Content-Type:

application/x-www-form-urlencoded


Send:

username=john@example.com
password=Test1234!


IMPORTANT:

Although the field is called `username`, send the user's EMAIL.


## Response

Example:

{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}


## Frontend action

After successful login:

1. Save the access_token.
2. Use it for protected API requests.


Example:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...


---

# 6. Authorization Header

All protected endpoints require:

Authorization: Bearer ACCESS_TOKEN


Example:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...


The frontend should NOT send:

user_id=1


The backend gets the current user's ID from the JWT token.


---

# 7. Get Current User's Meetings

## Endpoint

GET /meetings/

## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Purpose

Return meetings belonging to the logged-in user.


## Response

Example:

[
  {
    "id": 1,
    "title": "Weekly Team Meeting",
    "user_id": 1,
    "file_name": "meeting.mp3",
    "file_path": "uploads/meetings/abc.mp3",
    "transcript_text": "John said...",
    "summary_text": "The team discussed...",
    "status": "analyzed"
  }
]


IMPORTANT:

The frontend should use the authenticated user's token.

Do not allow the frontend to request another user's meetings.


---

# 8. Get One Meeting

## Endpoint

GET /meetings/{meeting_id}

Example:

GET /meetings/15


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Response

Example:

{
  "id": 15,
  "title": "Weekly Team Meeting",
  "user_id": 1,
  "file_name": "meeting.mp3",
  "file_path": "uploads/meetings/abc.mp3",
  "transcript_text": "John will finish the payment API.",
  "summary_text": "The team discussed the payment API.",
  "status": "analyzed"
}


If the meeting does not belong to the logged-in user:

{
  "detail": "Meeting not found"
}


HTTP status:

404


---

# 9. Upload Meeting Audio

## Endpoint

POST /meetings/upload

## Authentication

Required.

## Purpose

Upload and process a meeting recording.


## Request

Content-Type:

multipart/form-data


Fields:

title:
Weekly Team Meeting

file:
meeting.mp3


IMPORTANT:

Do NOT send user_id.

The backend gets the user ID from the JWT token.


## Headers

Authorization: Bearer ACCESS_TOKEN


## Example

POST /meetings/upload


Form Data:

title = Weekly Team Meeting
file = meeting.mp3


## Backend processing

The backend performs:

1. Save uploaded audio.
2. Transcribe audio using Gemini.
3. Get previous meeting context using MCP.
4. Send current transcript + previous context to the AI Agent.
5. Generate meeting summary.
6. Extract action items.
7. Extract assignees.
8. Extract deadlines.
9. Convert deadlines into database dates.
10. Save meeting to PostgreSQL.
11. Create tasks.
12. Detect context changes.
13. Save context changes.
14. Return the complete result.


Processing flow:

Audio
   ↓
Transcription
   ↓
Previous Context
   ↓
MCP
   ↓
AI Agent
   ↓
Summary + Tasks
   ↓
Context Continuity Analysis
   ↓
Database


## Frontend behavior

Uploading may take some time.

Display:

"Processing meeting..."


After success:

"Meeting processed successfully."


The frontend should disable the upload button while processing.


---

# 10. Upload Meeting Response

Example:

{
  "message": "Meeting processed successfully",
  "meeting_id": 21,
  "status": "analyzed",
  "summary": "The team discussed the payment API and QA testing.",
  "action_items": [
    {
      "task": "Finish the payment API",
      "assignee": "John",
      "deadline": "September 3, 2026"
    },
    {
      "task": "Finish the QA test plan",
      "assignee": "Sarah",
      "deadline": "August 30, 2026"
    }
  ],
  "created_tasks": [
    {
      "description": "Finish the payment API",
      "assigned_to": "John",
      "deadline": null,
      "status": "open",
      "meeting_id": 21
    }
  ],
  "context_changes": [
    {
      "id": 2,
      "change_type": "deadline",
      "task": "Payment API",
      "task_id": 33,
      "previous_value": "August 28, 2026",
      "new_value": "September 3, 2026",
      "evidence": "I will finish it by September 3, 2026 instead of August 28.",
      "status": "pending",
      "previous_meeting_id": 20,
      "meeting_id": 21
    }
  ]
}


IMPORTANT:

`created_tasks.deadline` can currently be `null` in some responses because the initial task creation and context-change confirmation are separate operations.

For a detected context change:

The frontend should NOT automatically update the task.

The frontend must display the Context Continuity Alert and wait for the user's decision.


---

# 11. Get All Tasks

## Endpoint

GET /tasks/

## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Purpose

Return tasks belonging to the logged-in user.


## Response

Example:

[
  {
    "id": 33,
    "description": "Finish the payment API",
    "assigned_to": "John",
    "deadline": "2026-08-28",
    "status": "open",
    "meeting_id": 20
  },
  {
    "id": 34,
    "description": "Finish the QA test plan",
    "assigned_to": "Sarah",
    "deadline": "2026-08-30",
    "status": "open",
    "meeting_id": 21
  }
]


IMPORTANT:

The backend automatically filters tasks by the logged-in user.


---

# 12. Get One Task

## Endpoint

GET /tasks/{task_id}

Example:

GET /tasks/33


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Response

Example:

{
  "id": 33,
  "description": "Finish the payment API",
  "assigned_to": "John",
  "deadline": "2026-08-28",
  "status": "open",
  "meeting_id": 20
}


---

# 13. Update Task

## Endpoint

PUT /tasks/{task_id}

Example:

PUT /tasks/33


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN

Content-Type:

application/json


## Request

Example:

{
  "status": "completed"
}


Another example:

{
  "description": "Finish the payment API and write tests",
  "status": "in_progress"
}


Another example:

{
  "deadline": "2026-09-03"
}


## Available fields

| Field | Type | Description |
|---|---|---|
| description | string | Task description |
| assigned_to | string | Person responsible |
| deadline | date | Task deadline |
| status | string | Task status |


## Response

Example:

{
  "id": 33,
  "description": "Finish the payment API",
  "assigned_to": "John",
  "deadline": "2026-09-03",
  "status": "open",
  "meeting_id": 20
}


IMPORTANT:

For normal task editing, the frontend can use this endpoint.

For Context Continuity changes, use the Context Continuity Confirm endpoint described below.


---

# 14. Delete Task

## Endpoint

DELETE /tasks/{task_id}

Example:

DELETE /tasks/33


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Response

Example:

{
  "message": "Task deleted successfully"
}


---

# 15. Task Status

The frontend can use statuses such as:

open

in_progress

completed


Example:

{
  "status": "completed"
}


The backend currently stores status as a string.


---

# 16. CONTEXT CONTINUITY

# 17. Get Context Continuity Changes

## Endpoint

GET /context-changes/

## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Purpose

Get context changes belonging to the logged-in user.


## Response

Example:

[
  {
    "id": 2,
    "meeting_id": 21,
    "previous_meeting_id": 20,
    "task_id": 33,
    "change_type": "deadline",
    "previous_value": "August 28, 2026",
    "new_value": "September 3, 2026",
    "evidence": "I will finish it by September 3, 2026 instead of August 28.",
    "status": "pending",
    "created_at": "2026-08-25T12:05:04.244665"
  }
]


---

# 18. Context Change Fields

| Field | Type | Description |
|---|---|---|
| id | integer | Context change ID |
| meeting_id | integer | Current meeting |
| previous_meeting_id | integer | Previous meeting where old information came from |
| task_id | integer | Related task |
| change_type | string | Type of change |
| previous_value | string | Previous value |
| new_value | string | New value |
| evidence | string | Transcript evidence explaining the change |
| status | string | pending, confirmed, or rejected |
| created_at | datetime | Time the change was detected |


Possible `change_type` values:

deadline

assignee

decision


Possible `status` values:

pending

confirmed

rejected


---

# 19. Get One Context Change

## Endpoint

GET /context-changes/{change_id}

Example:

GET /context-changes/2


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Response

Example:

{
  "id": 2,
  "meeting_id": 21,
  "previous_meeting_id": 20,
  "task_id": 33,
  "change_type": "deadline",
  "previous_value": "August 28, 2026",
  "new_value": "September 3, 2026",
  "evidence": "I will finish it by September 3, 2026 instead of August 28.",
  "status": "pending",
  "created_at": "2026-08-25T12:05:04.244665"
}


---

# 20. CONFIRM CONTEXT CHANGE

## Endpoint

POST /context-changes/{change_id}/confirm

Example:

POST /context-changes/2/confirm


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Purpose

Confirm the change detected by the AI.


Example:

Previous task:

Payment API
Deadline: August 28, 2026


Context change:

Payment API
New deadline: September 3, 2026


User clicks:

CONFIRM


The backend then updates the related task.


## Response

Example:

{
  "message": "Context change confirmed",
  "change_id": 2,
  "status": "confirmed",
  "updated_task_id": 33
}


After confirmation:

The task should contain:

{
  "id": 33,
  "description": "Finish the payment API",
  "assigned_to": "John",
  "deadline": "2026-09-03",
  "status": "open",
  "meeting_id": 20
}


## FRONTEND BEHAVIOR

After the user clicks Confirm:

1. Call:

POST /context-changes/{change_id}/confirm

2. Wait for successful response.

3. Remove the alert from the pending alerts list.

4. Refresh the task list.

5. Show a success message.

Example:

"Task deadline updated to September 3, 2026."


Do NOT update the task locally before the backend confirms the operation.


---

# 21. REJECT CONTEXT CHANGE

## Endpoint

POST /context-changes/{change_id}/reject

Example:

POST /context-changes/2/reject


## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN


## Purpose

Reject a context change.


Example:

Previous deadline:

August 28, 2026


Detected new deadline:

September 3, 2026


User clicks:

REJECT


The backend will:

1. Keep the existing task unchanged.
2. Mark the context change as rejected.


## Response

Example:

{
  "message": "Context change rejected",
  "change_id": 2,
  "status": "rejected"
}


## Frontend behavior

After successful rejection:

1. Remove the alert from the pending list.
2. Keep the existing task unchanged.
3. Show:

"Context change rejected."


---

The user must always have control over the change.

This Confirm/Reject flow is a core feature of the AI Meeting Agent.