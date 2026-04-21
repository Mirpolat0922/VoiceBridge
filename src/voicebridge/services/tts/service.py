from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.tts import SynthesizedSpeechResult
from voicebridge.services.tts.registry import TtsProviderRegistry


class TtsService:
    def __init__(
        self,
        *,
        registry: TtsProviderRegistry,
        default_provider_name: str,
    ) -> None:
        self._registry = registry
        self._default_provider_name = default_provider_name

    def synthesize(
        self,
        text: str,
        *,
        language: LanguageCode,
    ) -> SynthesizedSpeechResult:
        provider = self._registry.get(self._default_provider_name)
        return provider.synthesize(text, language=language)

    def cleanup_temporary_files(self, result: SynthesizedSpeechResult) -> None:
        for path in result.temporary_paths:
            path.unlink(missing_ok=True)
