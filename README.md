# ai-meeting-agent
AI-powered meeting assistant that transcribes meetings, summarizes discussions, retrieves previous meeting context using MCP, and extracts actionable tasks with assignees and deadlines.


# After Postgress logic flow
1. PostgreSQL
      ↓
2. Models
      ↓
3. Alembic migrations
      ↓
4. CRUD APIs
      ↓
5. File upload        ← MP3/WAV/M4A/TXT
      ↓
6. Gemini
      ↓
7. Transcription
      ↓
8. Summary + Action Items
      ↓
9. MCP context