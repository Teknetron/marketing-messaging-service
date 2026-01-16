# src/marketing_messaging_service/main.py

from fastapi import FastAPI

app = FastAPI(title="Marketing Messaging Service")

# routers will be added later


@app.get("/health")
def health_check():
    return {"status": "ok"}
