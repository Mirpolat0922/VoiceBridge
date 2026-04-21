from pathlib import Path

from pydantic import BaseModel, ConfigDict

from voicebridge.domain.languages import LanguageCode


class SynthesizedSpeechResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_name: str
    language: LanguageCode
    source_text: str
    voice_path: Path
    temporary_paths: tuple[Path, ...] = ()
