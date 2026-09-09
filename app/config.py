from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    perplexity_api_key: str = ""
    gemini_api_key: str = ""
    xai_api_key: str = ""

    kakao_rest_key: str = ""
    naver_client_id: str = ""
    naver_client_secret: str = ""
    google_places_key: str = ""

    mention_threshold_yes: int = 10
    mention_threshold_partial: int = 3

    http_timeout: float = 8.0

    # 관리자 전용 엔드포인트 보호. 미설정이면 해당 엔드포인트는 닫힌다.
    admin_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
