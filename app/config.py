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

    # 주간 리포트 발송 (Resend). 미설정이면 발송을 건너뛴다.
    resend_api_key: str = ""
    resend_from: str = ""
    # 메일에 넣을 대시보드·수신거부 링크의 기준 주소
    public_base_url: str = "http://localhost:3001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
