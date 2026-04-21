from pathlib import Path

from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.services.user_settings import UserSettingsService
from voicebridge.storage.database import Database
from voicebridge.storage.user_settings_repository import UserSettingsRepository


def build_service(database_path: Path) -> UserSettingsService:
    database = Database(database_path)
    database.initialize()

    repository = UserSettingsRepository(database)
    return UserSettingsService(
        repository=repository,
        default_source_language="auto",
        default_target_language="ru",
        default_reply_mode="text_and_voice",
    )


def test_get_or_create_returns_default_settings(tmp_path: Path) -> None:
    service = build_service(tmp_path / "voicebridge.db")

    settings = service.get_or_create(telegram_user_id=123)

    assert settings.telegram_user_id == 123
    assert settings.source_language is LanguageCode.AUTO
    assert settings.target_language is LanguageCode.RU
    assert settings.reply_mode is ReplyMode.TEXT_AND_VOICE
    assert settings.uzbek_beta_notice_enabled is True


def test_update_persists_changed_settings(tmp_path: Path) -> None:
    service = build_service(tmp_path / "voicebridge.db")

    updated = service.update(
        telegram_user_id=123,
        source_language=LanguageCode.EN,
        target_language=LanguageCode.UZ,
        reply_mode=ReplyMode.TEXT_ONLY,
        uzbek_beta_notice_enabled=False,
    )

    assert updated.source_language is LanguageCode.EN
    assert updated.target_language is LanguageCode.UZ
    assert updated.reply_mode is ReplyMode.TEXT_ONLY
    assert updated.uzbek_beta_notice_enabled is False
