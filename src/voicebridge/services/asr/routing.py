from voicebridge.domain.languages import LanguageCode


class AsrRouter:
    def __init__(
        self,
        *,
        uz_provider: str,
        ru_provider: str,
        en_provider: str,
    ) -> None:
        self._provider_map = {
            LanguageCode.UZ: uz_provider,
            LanguageCode.RU: ru_provider,
            LanguageCode.EN: en_provider,
        }

    def resolve_provider_name(self, requested_language: LanguageCode) -> str:
        return self._provider_map[requested_language]
