from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VOICEBRIDGE_",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = Field(..., description="Telegram bot token.")
    log_level: str = Field(default="INFO", description="Application log level.")
    db_path: Path = Field(default=Path("voicebridge.db"), description="SQLite database path.")
    storage_dir: Path = Field(default=Path("data"), description="Application storage directory.")
    whisper_model_size: str = Field(default="small", description="Whisper model size.")
    whisper_device: str = Field(default="auto", description="Inference device for faster-whisper.")
    whisper_compute_type: str = Field(
        default="int8",
        description="Compute type for faster-whisper inference.",
    )
    asr_provider_uz: str = Field(
        default="nemo_uzbek",
        description="ASR provider used for Uzbek.",
    )
    asr_provider_ru: str = Field(
        default="faster_whisper",
        description="ASR provider used for Russian.",
    )
    asr_provider_en: str = Field(
        default="faster_whisper",
        description="ASR provider used for English.",
    )
    nemo_uzbek_model_name: str = Field(
        default="nvidia/stt_uz_fastconformer_hybrid_large_pc",
        description="NeMo model name for Uzbek ASR.",
    )
    groq_api_key: str = Field(
        default="",
        description="Groq API key used for transcript post-processing and translation.",
    )
    groq_model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model used for transcript post-processing and translation.",
    )
    groq_endpoint: str = Field(
        default="https://api.groq.com/openai/v1/chat/completions",
        description="Groq OpenAI-compatible chat completions endpoint.",
    )
    groq_max_attempts: int = Field(
        default=2,
        description="Maximum attempts for Groq requests.",
    )
    groq_retry_base_delay_seconds: float = Field(
        default=1.0,
        description="Base delay for Groq retry backoff.",
    )
    groq_max_completion_tokens: int = Field(
        default=300,
        description="Maximum completion tokens requested from Groq text generation calls.",
    )
    default_source_language: str = Field(
        default="ru",
        description="Default source language for new users.",
    )
    default_target_language: str = Field(
        default="ru",
        description="Default target language for new users.",
    )
    default_reply_mode: str = Field(
        default="text_only",
        description="Default reply mode for new users.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
