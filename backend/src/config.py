"""
TrainingPlan Backend Configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    # Application
    app_name: str = "TrainingPlan"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str
    db_echo: bool = False  # Set to True to log SQL queries
    
    # Redis
    redis_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # Short expiry in production
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12
    
    @property
    def effective_token_expire_minutes(self) -> int:
        """Return longer token expiry in development mode for easier testing."""
        if self.environment == "development":
            return 60 * 24 * 7  # 7 days in development
        return self.access_token_expire_minutes
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # File Upload
    upload_dir: str = "/app/uploads"
    max_upload_size: int = 50  # MB
    allowed_extensions: str = "tcx,fit,gpx"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions from comma-separated string."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    # External Integrations - Garmin
    garmin_client_id: str = ""
    garmin_client_secret: str = ""
    garmin_redirect_uri: str = ""
    garmin_api_base_url: str = "https://apis.garmin.com"
    
    # External Integrations - TrainingPeaks
    trainingpeaks_api_key: str = ""
    trainingpeaks_client_id: str = ""
    trainingpeaks_client_secret: str = ""
    trainingpeaks_api_base_url: str = "https://api.trainingpeaks.com/v2"
    
    # External Integrations - Strava
    strava_client_id: str = ""
    strava_client_secret: str = ""
    strava_redirect_uri: str = ""
    strava_api_base_url: str = "https://www.strava.com/api/v3"
    
    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    celery_timezone: str = "Europe/Berlin"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


# Global settings instance
settings = Settings()
