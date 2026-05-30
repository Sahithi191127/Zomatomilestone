"""Environment-driven settings (Cross-Cutting Concerns — Configuration)."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root (parent of `src/`) — stable paths on Streamlit Cloud regardless of cwd quirks
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    hf_dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"
    data_path: Path = Path("data/processed/restaurants.parquet")

    budget_low_max: float = 500.0
    budget_medium_max: float = 1500.0

    max_candidates: int = 30
    max_additional_preferences_length: int = 500
    location_match_mode: str = "substring"  # substring | exact

    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com"

    # Comma-separated origins for FastAPI CORS (e.g. Vercel production + preview URLs)
    cors_origins: str = ""

    @field_validator("data_path", mode="before")
    @classmethod
    def _resolve_data_path(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path.resolve()


settings = Settings()

_DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def get_cors_origins() -> list[str]:
    """Local dev defaults plus optional CORS_ORIGINS env (Railway / .env)."""
    extra = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    merged: list[str] = []
    seen: set[str] = set()
    for origin in (*_DEFAULT_CORS_ORIGINS, *extra):
        if origin not in seen:
            seen.add(origin)
            merged.append(origin)
    return merged
