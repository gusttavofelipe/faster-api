from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FASTER_API"
    APP_TITLE: str = "TITLE"
    APP_VERSION: str = "0.0.1"
    APP_DESCRIPTION: str = "DESCRIPTION"
    
    DATABASE_URL: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_PORT: str = ""
    DATABASE_URL: str = ""

    REDIS_URL: str = ""
    REDIS_PASSWORD: str = ""

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")


settings: Settings = Settings()
