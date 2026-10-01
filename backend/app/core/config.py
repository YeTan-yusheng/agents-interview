from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "agents-interview"
    debug: bool = False
    # 数据库配置
    database_url: str # 必填。缺失启动报错
    # 日志配置
    log_level: str = "INFO"
    # JWT配置
    jwt_secret: str  # 必填。缺失启动报错
    # 令牌过期时间（分钟）配置
    token_expire_minutes: int = 120
    # 测试数据库配置
    test_database_url: str = ""
    # LLM配置
    llm_api_key: str # 必填。缺失启动报错
    llm_base_url: str # 必填。缺失启动报错
    llm_model: str = "deepseek-r1"
    # 最大轮数
    max_rounds: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
