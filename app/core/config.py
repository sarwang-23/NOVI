from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str

    # AI/ML team service (backend forwards requests, does NOT implement logic)
    AIML_API_URL: Optional[str] = "http://localhost:9000"
    AIML_API_KEY: Optional[str] = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
