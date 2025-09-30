"""
환경변수 기반 설정 관리

Pydantic Settings가 자동으로 다음 순서로 환경변수를 로드합니다:
1. 시스템 환경변수 (/etc/environment, export 등)
2. .env 파일 (선택사항)
3. 클래스 기본값

BaseSettings를 상속하면 별도의 os.getenv() 호출 없이 자동으로
같은 이름의 환경변수를 읽어옵니다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 설정

    각 필드는 자동으로 동일한 이름의 환경변수에서 값을 읽습니다.
    예: MONGODB_URL 환경변수 → settings.MONGODB_URL
    """

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017/"
    MONGODB_DATABASE: str = "simulverse"

    # JWT Security
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Token expiration (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Application
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Optional: Advanced
    CORS_ORIGINS: Optional[str] = None
    MAX_UPLOAD_SIZE: int = 10  # MB
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # 추가 환경변수 무시
        env_ignore_empty=True  # 빈 환경변수 무시
    )

    def get_cors_origins(self) -> list:
        """CORS origins를 리스트로 반환"""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return []


# 전역 설정 인스턴스
settings = Settings()


# 하위 호환성을 위한 별칭 (기존 코드와의 호환)
MONGODB_URL = settings.MONGODB_URL
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
