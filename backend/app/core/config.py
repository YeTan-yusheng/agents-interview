from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "agents-interview"
    debug: bool = False
    database_url: str # 必填。缺失启动报错
    log_level: str = "INFO"
    jwt_secret: str  # 必填。缺失启动报错
    token_expire_minutes: int = 120

    test_database_url: str = ""

    llm_api_key: str # 必填。缺失启动报错
    llm_base_url: str # 必填。缺失启动报错
    llm_model: str = "deepseek-r1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
