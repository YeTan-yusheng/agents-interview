from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "agents-interview"
    debug: bool = False
    database_url: str
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

settings = Settings()


