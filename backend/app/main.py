from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.users import router as user_router
from app.routes.meetings import router as meeting_router
from app.routes.tasks import router as task_router
from app.routes.auth import router as auth_router


app = FastAPI(title="AI Meeting Agent")


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(user_router)
app.include_router(meeting_router)
app.include_router(task_router)
app.include_router(auth_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Meeting Agent API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }