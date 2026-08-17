import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "PusulamNet"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pusulamnet.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pusulamnet-secret-key-change-in-production")

    
    # İstatistiksel Analiz Eşik Değerleri (Thresholds)
    STD_STABLE_THRESHOLD: float = 2.0      # <= 2.0 ise "İstikrarlı"
    STD_MODERATE_THRESHOLD: float = 5.0    # 2.0 < std <= 5.0 ise "Orta düzeyde dalgalı", > 5.0 ise "Dalgalı"
    
    PERIOD_CHANGE_SIGNIFICANT: float = 3.0 # Dönemsel değişim bariz artış/düşüş eşiği
    
    MIN_EXAMS_FOR_PERIOD_ANALYSIS: int = 6  # Son 3 vs Önceki 3 analizi için gereken min deneme
    MIN_EXAMS_FOR_STABILITY_ANALYSIS: int = 5 # Standart sapma için min deneme
    MIN_EXAMS_FOR_TREND: int = 3           # Genel eğilim yorumu için min deneme

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
