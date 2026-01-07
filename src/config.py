from dataclasses import dataclass
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


@dataclass(frozen=True)
class AppConfig:
    shorts_per_day: int = 4
    short_duration_seconds: int = 12
    question_duration_seconds: int = 10
    answer_duration_seconds: int = 2
    max_daily_uploads: int = 5
    retry_backoff_seconds: int = 15
    max_generation_attempts: int = 5
    locale: str = "en"
    voice: str = "en-US-JennyNeural"
    timezone: str = "UTC"


@dataclass(frozen=True)
class Keys:
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    openrouter_key: str | None = os.getenv("OPENROUTER_KEY")
    unsplash_access_key: str | None = os.getenv("UNSPLASH_ACCESS_KEY")
    pexels_api_key: str | None = os.getenv("PEXELS_API_KEY")
    pixabay_api_key: str | None = os.getenv("PIXABAY_API_KEY")
    youtube_api_key: str | None = os.getenv("YOUTUBE_API_KEY")
    yt_client_id: str | None = os.getenv("YT_CLIENT_ID_1")
    yt_client_secret: str | None = os.getenv("YT_CLIENT_SECRET_1")
    yt_refresh_token: str | None = os.getenv("YT_REFRESH_TOKEN_1")


CONFIG = AppConfig()
KEYS = Keys()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
