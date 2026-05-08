from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AI_MODEL: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: str | None = None
    WEATHER_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()