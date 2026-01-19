import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    api_host: str = os.environ.get("API_HOST", "127.0.0.1")
    api_port: int = int(os.environ.get("API_PORT", 8000))

    @property
    def database_url(self) -> str:
        # `settings.py` is at: `.../src/marketing_messaging_service/config/settings.py`
        # Repo root is 4 levels up: config -> marketing_messaging_service -> src -> repo
        repo_root = Path(__file__).resolve().parents[3]
        default_db_path = (repo_root / "messaging.db").resolve()

        env_url = os.environ.get("DATABASE_URL")
        if not env_url:
            return f"sqlite:///{default_db_path}"

        # If someone sets a relative sqlite URL, normalize it to the repo root.
        if env_url.startswith("sqlite:///./"):
            rel = env_url.removeprefix("sqlite:///./")
            return f"sqlite:///{(repo_root / rel).resolve()}"

        return env_url


settings = Settings()
