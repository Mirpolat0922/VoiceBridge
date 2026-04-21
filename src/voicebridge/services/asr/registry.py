from voicebridge.services.asr.base import AsrProvider
from voicebridge.services.asr.exceptions import AsrError


class AsrProviderRegistry:
    def __init__(self, providers: list[AsrProvider]) -> None:
        self._providers = {provider.name: provider for provider in providers}

    def get(self, provider_name: str) -> AsrProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            available = ", ".join(sorted(self._providers))
            raise AsrError(
                f"Unknown ASR provider '{provider_name}'. Available providers: {available}"
            )
        return provider
