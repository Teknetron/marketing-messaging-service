import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    api_host: str = os.environ.get("API_HOST", "127.0.0.1")
    api_port: int = int(os.environ.get("API_PORT", 8000))


settings = Settings()
