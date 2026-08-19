from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Adding extra ignore to prevent pydantic errors with extra env vars

settings = Settings()
