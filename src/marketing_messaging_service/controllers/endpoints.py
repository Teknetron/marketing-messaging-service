from fastapi import FastAPI

from src.marketing_messaging_service.controllers.audit_controller import \
    router as audit_router
from src.marketing_messaging_service.controllers.event_controller import \
    router as event_router

app = FastAPI(title="Marketing Messaging Service")

# include routers
app.include_router(event_router)
app.include_router(audit_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
