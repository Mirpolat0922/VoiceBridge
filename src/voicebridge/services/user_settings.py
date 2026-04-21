from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.schemas.user_settings import UserSettings
from voicebridge.storage.user_settings_repository import UserSettingsRepository


class UserSettingsService:
    def __init__(
        self,
        repository: UserSettingsRepository,
        default_source_language: str,
        default_target_language: str,
        default_reply_mode: str,
    ) -> None:
        self._repository = repository
        self._default_source_language = LanguageCode(default_source_language)
        self._default_target_language = LanguageCode(default_target_language)
        self._default_reply_mode = ReplyMode(default_reply_mode)

    def get_or_create(self, telegram_user_id: int) -> UserSettings:
        settings = self._repository.get_by_user_id(telegram_user_id)
        if settings is not None:
            return settings

        default_settings = UserSettings(
            telegram_user_id=telegram_user_id,
            source_language=self._default_source_language,
            target_language=self._default_target_language,
            reply_mode=self._default_reply_mode,
        )
        return self._repository.upsert(default_settings)

    def update(
        self,
        telegram_user_id: int,
        *,
        source_language: LanguageCode | None = None,
        target_language: LanguageCode | None = None,
        reply_mode: ReplyMode | None = None,
        uzbek_beta_notice_enabled: bool | None = None,
    ) -> UserSettings:
        current = self.get_or_create(telegram_user_id)

        updated = current.model_copy(
            update={
                "source_language": source_language or current.source_language,
                "target_language": target_language or current.target_language,
                "reply_mode": reply_mode or current.reply_mode,
                "uzbek_beta_notice_enabled": (
                    uzbek_beta_notice_enabled
                    if uzbek_beta_notice_enabled is not None
                    else current.uzbek_beta_notice_enabled
                ),
            }
        )
        return self._repository.upsert(updated)
