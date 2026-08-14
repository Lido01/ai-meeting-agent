from fastapi import FastAPI
from app.routes.users import router as user_router
from app.routes.meetings import router as meeting_router
from app.routes.tasks import router as task_router

app = FastAPI(title="AI Meeting Agent")

# Include the routers for users and meetings, Task
app.include_router(user_router)
app.include_router(meeting_router)
app.include_router(task_router)

@app.get("/")
def root():
    return {"message": "AI Meeting Agent API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}