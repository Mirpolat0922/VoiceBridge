from functools import cached_property

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.audio import NormalizedAudio
from voicebridge.schemas.transcription import TranscriptionResult
from voicebridge.services.asr.base import AsrProvider
from voicebridge.services.asr.exceptions import AsrError


class NemoUzbekAsrProvider(AsrProvider):
    def __init__(self, *, model_name: str) -> None:
        self._model_name = model_name

    @property
    def name(self) -> str:
        return "nemo_uzbek"

    @cached_property
    def _model(self) -> object:
        try:
            import nemo.collections.asr as nemo_asr
        except ImportError as error:  # pragma: no cover - depends on optional runtime environment
            raise AsrError(
                "NeMo ASR is not installed. Install the Uzbek ASR extra to use this provider."
            ) from error

        try:
            return nemo_asr.models.ASRModel.from_pretrained(self._model_name)
        except Exception as error:  # pragma: no cover - external model boundary
            raise AsrError(f"Failed to load NeMo Uzbek model '{self._model_name}'.") from error

    def transcribe(
        self,
        audio: NormalizedAudio,
        *,
        requested_language: LanguageCode,
    ) -> TranscriptionResult:
        try:
            result = self._model.transcribe([str(audio.normalized_path)])[0]
        except Exception as error:  # pragma: no cover - external model boundary
            raise AsrError("NeMo Uzbek transcription failed.") from error

        text = result.text if hasattr(result, "text") else str(result)
        text = text.strip()
        if not text:
            raise AsrError("No speech was recognized in the audio.")

        return TranscriptionResult(
            text=text,
            provider_name=self.name,
            audio_path=audio.normalized_path,
            requested_language=requested_language,
            detected_language=LanguageCode.UZ,
        )
