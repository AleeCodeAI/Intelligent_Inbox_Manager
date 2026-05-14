from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class MainSettings(BaseSettings):
    """Configuration for LLM-related settings."""

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    # ------------------- OpenRouter API Keys and URLs ------------------ #
    OPENROUTER_API_KEY: str
    OPENROUTER_URL: str

    # ------------------- Model Names ------------------ #
    GPT_NANO_MODEL: str = "openai/gpt-4.1-nano"
    GPT_OSS_MODEL: str = "openai/gpt-oss-120b"
    GEMMA_MODEL: str = "google/gemma-4-26b-a4b-it"


if __name__ == "__main__":
    config = MainSettings()
    print(config.OPENROUTER_URL)
