@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import FastAPI
from app.routes.users import router as user_router

app = FastAPI(title="AI Meeting Agent")

app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "AI Meeting Agent API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}