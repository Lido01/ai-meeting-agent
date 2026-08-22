# AI Meeting Agent — API Endpoints

## 1. Overview

The flow is:

Frontend
   ↓
FastAPI Backend
   ↓
PostgreSQL
   ↓
Gemini / MCP
   ↓
FastAPI
   ↓
Frontend

---

# 2. Authentication

The application uses JWT authentication.

The frontend must:

1. Register a user.
2. Login.
3. Receive an access token.
4. Store the token.
5. Send the token with protected API requests.

Protected requests use:

Authorization: Bearer YOUR_ACCESS_TOKEN


---

# 3. User Registration

## Endpoint

POST /users/

## Purpose

Create a new user account.

## Authentication

Not required.

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

Important:

The backend does NOT return the password.

The backend stores a hashed password.

---

# 4. Login

## Endpoint

POST /auth/login

## Purpose

Login a user and receive a JWT access token.

## Authentication

Not required.

## Request

This endpoint uses form data.

Content-Type:

application/x-www-form-urlencoded

The frontend sends:

username=john@example.com
password=Test1234!

Important:

Although the field is called "username", send the user's EMAIL.

## Response

Example:

{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

## Frontend action

After successful login:

1. Save access_token.
2. Use it for protected requests.

Example:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...


---

# 5. Authorization Header

All protected endpoints require:

Authorization: Bearer ACCESS_TOKEN

Example:

Authorization: Bearer eyJhbGciOiJIUzI1NiIs...


The frontend should NOT send:

user_id=1

The backend gets the current user's ID from the JWT token.


---

# 6. Get Current User's Meetings

## Endpoint

GET /meetings/

## Authentication

Required.

## Request

Headers:

Authorization: Bearer ACCESS_TOKEN

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
    "status": "analyzed",
    "tasks": []
  }
]

## Important

The frontend does NOT send user_id.

The backend automatically gets the logged-in user from JWT.


---

# 7. Get One Meeting

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
  "transcript_text": "John will finish...",
  "summary_text": "The team discussed the payment API.",
  "status": "analyzed",
  "tasks": [
    {
      "id": 10,
      "description": "Finish the payment API",
      "assigned_to": "John",
      "deadline": null,
      "status": "open",
      "meeting_id": 15
    }
  ]
}

If the meeting does not belong to the logged-in user:

404 Meeting not found

---

# 8. Upload Meeting Audio

## Endpoint

POST /meetings/upload

## Authentication

Required.

## Purpose

Upload a meeting recording.

The backend then:

1. Saves the audio file.
2. Sends the file to Gemini.
3. Generates the transcript.
4. Gets previous meeting context.
5. Sends transcript + context to the AI Agent.
6. Generates summary.
7. Extracts action items.
8. Converts deadlines.
9. Saves the meeting.
10. Creates tasks.
11. Saves tasks in PostgreSQL.
12. Returns the result.

## Request

Content-Type:

multipart/form-data

Fields:

title:
Weekly Team Meeting

file:
meeting.mp3

Important:

Do NOT send user_id.

The backend gets the user ID from the JWT token.

## Example

POST /meetings/upload

Form Data:

title = Weekly Team Meeting
file = meeting.mp3

Headers:

Authorization: Bearer ACCESS_TOKEN

## Response

Example:

{
  "message": "Meeting processed successfully",
  "meeting_id": 15,
  "status": "analyzed",
  "summary": "The team discussed the payment API and QA testing.",
  "action_items": [
    {
      "task": "Finish the payment API",
      "assignee": "John",
      "deadline": null
    },
    {
      "task": "Prepare the QA test plan",
      "assignee": "Sarah",
      "deadline": null
    }
  ],
  "created_tasks": [
    {
      "description": "Finish the payment API",
      "assigned_to": "John",
      "deadline": null,
      "status": "open"
    },
    {
      "description": "Prepare the QA test plan",
      "assigned_to": "Sarah",
      "deadline": null,
      "status": "open"
    }
  ]
}

## Frontend behavior

Uploading may take some time because the backend is:

Audio/Text file
 ↓
Transcription
 ↓
AI analysis
 ↓
Task extraction
 ↓
Database save

The frontend should show a loading message:

"Processing meeting..."

After success:

"Meeting processed successfully."


---

# 9. Get All Tasks

## Endpoint

GET /tasks/

## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN

## Response

Example:

[
  {
    "id": 10,
    "description": "Finish the payment API",
    "assigned_to": "John",
    "deadline": null,
    "status": "open",
    "meeting_id": 15
  },
  {
    "id": 11,
    "description": "Prepare the QA test plan",
    "assigned_to": "Sarah",
    "deadline": null,
    "status": "open",
    "meeting_id": 15
  }
]

## Important

The backend automatically returns only tasks belonging to the logged-in user.


---

# 10. Get One Task

## Endpoint

GET /tasks/{task_id}

Example:

GET /tasks/10

## Authentication

Required.

## Headers

Authorization: Bearer ACCESS_TOKEN

## Response

Example:

{
  "id": 10,
  "description": "Finish the payment API",
  "assigned_to": "John",
  "deadline": null,
  "status": "open",
  "meeting_id": 15
}


---

# 11. Update Task

## Endpoint

PUT /tasks/{task_id}

Example:

PUT /tasks/10

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
  "id": 10,
  "description": "Finish the payment API",
  "assigned_to": "John",
  "deadline": null,
  "status": "completed",
  "meeting_id": 15
}


---

# 12. Delete Task

## Endpoint

DELETE /tasks/{task_id}

Example:

DELETE /tasks/10

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

# 13. Task Status

The frontend can use statuses such as:

open

in_progress

completed

The backend currently stores the status as a string.

Example:

{
  "status": "completed"
}


---

# 14. Error Responses

## 401 Unauthorized

Example:

{
  "detail": "Invalid or expired token"
}

Meaning:

The JWT is missing, invalid, or expired.

Frontend action:

Redirect the user to the login page.


---

## 404 Not Found

Example:

{
  "detail": "Task not found"
}

or:

{
  "detail": "Meeting not found"
}

Meaning:

The requested resource does not exist or does not belong to the logged-in user.


---

## 400 Bad Request

Example:

{
  "detail": "Email already registered"
}

Meaning:

The request contains invalid data or the email already exists.


---

## 422 Validation Error

FastAPI may return:

{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address"
    }
  ]
}

Meaning:

The frontend sent invalid data.

The frontend should show a validation message to the user.


---