from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./deception.db"
    # Bearer token for the dashboard / admin API. Required in production.
    admin_token: str = Field(default="", description="Bearer token for /api/v1/*")
    # Shared secret between canary-listener and API for /internal/v1/*.
    internal_api_key: str = ""
    # Public base URL of the canary listener, embedded in tokens.
    canary_base_url: str = "http://localhost:8081"
    elasticsearch_url: str = ""
    elasticsearch_index_prefix: str = "deception-events"
    # Either basic auth or an API key (base64 "id:key"); empty = unauthenticated (dev only).
    elasticsearch_user: str = ""
    elasticsearch_password: str = ""
    elasticsearch_api_key: str = ""
    elasticsearch_ca_file: str = ""
    # Reverse proxies in front of the API that append to X-Forwarded-For
    # (ingress + UI nginx = 2 in the Helm chart). Used for login-failure limiting.
    trusted_proxy_count: int = 0
    auth_fail_limit: int = 10
    auth_fail_window_seconds: int = 300
    webhook_url: str = ""
    geoip_db_path: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    cors_origins: str = ""
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
