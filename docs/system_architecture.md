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