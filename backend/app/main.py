from fastapi import FastAPI

app = FastAPI(title="AI Meeting Agent")


@app.get("/")
def root():
    return {"message": "AI Meeting Agent API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}