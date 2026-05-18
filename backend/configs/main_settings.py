from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class MainSettings(BaseSettings):
    """Configuration for LLM-related settings."""

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    # ------------------- OpenRouter API Keys and URLs ------------------ #
    OPENROUTER_API_KEY: str
    OPENROUTER_URL: str

    # ------------------- Langfuse Keys and URL  ------------------ #
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str

    # ------------------- Groq API Keys and URLs ------------------ #
    GROQ_API_KEY: str
    GROQ_URL: str

    # ------------------- n8n webhook URL ------------------ #
    N8N_GET_EMAILS_WEBHOOK_URL:str
    SEND_EXAMPLE_EMAILS_N8N_URL: str

    # ------------------- Postgressl credentials ------------------ #
    POSTGRESQL_URL: str

    # ------------------- Model Names ------------------ #
    GPT_NANO_MODEL: str = "openai/gpt-4.1-nano"
    GPT_OSS_MODEL: str = "openai/gpt-oss-120b"
    GEMMA_MODEL: str = "google/gemma-4-26b-a4b-it"
    GROQ_JUDGE_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # ------------------- LLM Limits ------------------ #
    RAG_MAX_OUTPUT_RETRIES: int = 3

    # ------------------- Model Openrouter Pricing ------------------ #
    GPT_OSS_INPUT_PRICE: float = 0.039
    GPT_OSS_OUTPUT_PRICE: float = 0.18
    GPT_NANO_INPUT_PRICE: float = 0.10
    GPT_NANO_OUTPUT_PRICE: float = 0.40

if __name__ == "__main__":
    config = MainSettings()
    print(config.OPENROUTER_URL)
