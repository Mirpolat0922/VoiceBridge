from pydantic import BaseModel, ConfigDict

from voicebridge.domain.languages import LanguageCode


class TextPipelineResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_name: str
    source_language: LanguageCode
    target_language: LanguageCode
    source_text: str
    translated_text: str
