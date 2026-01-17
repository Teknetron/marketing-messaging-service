from src.marketing_messaging_service.controllers.event_controller import router as event_router
from src.marketing_messaging_service.controllers.audit_controller import router as audit_router

__all__ = ["event_router", "audit_router"]
