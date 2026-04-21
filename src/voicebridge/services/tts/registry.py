from voicebridge.services.tts.base import TtsProvider
from voicebridge.services.tts.exceptions import TtsError


class TtsProviderRegistry:
    def __init__(self, providers: list[TtsProvider]) -> None:
        self._providers = {provider.name: provider for provider in providers}

    def get(self, provider_name: str) -> TtsProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            available = ", ".join(sorted(self._providers))
            raise TtsError(
                f"Unknown TTS provider '{provider_name}'. Available providers: {available}"
            )
        return provider
