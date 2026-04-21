from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.audio import NormalizedAudio
from voicebridge.schemas.transcription import TranscriptionResult
from voicebridge.services.asr.registry import AsrProviderRegistry
from voicebridge.services.asr.routing import AsrRouter


class AsrService:
    def __init__(
        self,
        *,
        registry: AsrProviderRegistry,
        router: AsrRouter,
    ) -> None:
        self._registry = registry
        self._router = router

    def transcribe(
        self,
        audio: NormalizedAudio,
        *,
        requested_language: LanguageCode,
    ) -> TranscriptionResult:
        provider_name = self._router.resolve_provider_name(requested_language)
        provider = self._registry.get(provider_name)
        return provider.transcribe(audio, requested_language=requested_language)
