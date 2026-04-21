from functools import cached_property

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.audio import NormalizedAudio
from voicebridge.schemas.transcription import TranscriptionResult
from voicebridge.services.asr.base import AsrProvider
from voicebridge.services.asr.exceptions import AsrError


class FasterWhisperAsrProvider(AsrProvider):
    def __init__(
        self,
        *,
        model_size: str,
        device: str,
        compute_type: str,
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type

    @property
    def name(self) -> str:
        return "faster_whisper"

    @cached_property
    def _model(self) -> object:
        try:
            from faster_whisper import WhisperModel
        except ImportError as error:  # pragma: no cover - depends on runtime environment
            raise AsrError(
                "faster-whisper is not installed. Reinstall project dependencies to use ASR."
            ) from error

        return WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
        )

    def transcribe(
        self,
        audio: NormalizedAudio,
        *,
        requested_language: LanguageCode,
    ) -> TranscriptionResult:
        language = None if requested_language is LanguageCode.AUTO else requested_language.value

        try:
            segments, info = self._model.transcribe(
                str(audio.normalized_path),
                language=language,
                vad_filter=True,
            )
        except Exception as error:  # pragma: no cover - model execution boundary
            raise AsrError("faster-whisper transcription failed.") from error

        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise AsrError("No speech was recognized in the audio.")

        detected_language = None
        if getattr(info, "language", None):
            try:
                detected_language = LanguageCode(info.language)
            except ValueError:
                detected_language = None

        return TranscriptionResult(
            text=text,
            provider_name=self.name,
            audio_path=audio.normalized_path,
            requested_language=requested_language,
            detected_language=detected_language,
        )
