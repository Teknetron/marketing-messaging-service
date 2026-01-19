import uvicorn

from src.marketing_messaging_service.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.marketing_messaging_service.controllers.endpoints:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )