# API endpoints

Base URL: `http://localhost:8000`

Interactive API documentation is available at `http://localhost:8000/docs` when the FastAPI server is running.

## Meetings

### Get all meetings

`GET /meetings/`

Returns all meetings, ordered from newest to oldest.

```bash
curl http://localhost:8000/meetings/
```

Success response (`200 OK`):

```json
[
  {
    "id": 1,
    "title": "Product planning",
    "user_id": 1,
    "transcript_text": null,
    "summary_text": null,
    "status": "processing"
  }
]
```

### Get a meeting by ID

`GET /meetings/{meeting_id}`

Replace `{meeting_id}` with the meeting ID.

```bash
curl http://localhost:8000/meetings/1
```

Success response (`200 OK`):

```json
{
  "id": 1,
  "title": "Product planning",
  "user_id": 1,
  "transcript_text": null,
  "summary_text": null,
  "status": "processing"
}
```

If the ID does not exist, the API returns `404 Not Found`:

```json
{
  "detail": "Meeting not found"
}
```

### Create a meeting

`POST /meetings/`

```json
{
  "title": "Product planning",
  "user_id": 1
}
```

## Other available URLs

| Method | URL | Description |
| --- | --- | --- |
| `GET` | `/` | API status message |
| `GET` | `/health` | Health check |
| `POST` | `/users/` | Create a user |
| `GET` | `/docs` | Swagger UI documentation |
