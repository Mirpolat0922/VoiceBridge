from pathlib import Path

from pydantic import BaseModel, ConfigDict

from voicebridge.domain.languages import LanguageCode


class TranscriptionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    provider_name: str
    audio_path: Path
    requested_language: LanguageCode
    detected_language: LanguageCode | None = None
