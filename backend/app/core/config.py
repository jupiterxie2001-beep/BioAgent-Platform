from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    redis_url: str
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    storage_path: str = "../storage"
    celery_broker_url: str
    celery_result_backend: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
