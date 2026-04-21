from pathlib import Path

from pydantic import BaseModel, ConfigDict


class DownloadedAudio(BaseModel):
    model_config = ConfigDict(frozen=True)

    telegram_file_id: str
    original_path: Path
    original_format: str
    duration_seconds: int | None = None


class NormalizedAudio(BaseModel):
    model_config = ConfigDict(frozen=True)

    telegram_file_id: str
    source_path: Path
    normalized_path: Path
    sample_rate_hz: int
    channels: int
