import sqlite3
from pathlib import Path

from voicebridge.domain.languages import LanguageCode
from voicebridge.storage.database import Database
from voicebridge.storage.user_settings_repository import UserSettingsRepository


def test_database_initialize_migrates_legacy_auto_source_language(tmp_path: Path) -> None:
    database_path = tmp_path / "voicebridge.db"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE user_settings (
            telegram_user_id INTEGER PRIMARY KEY,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            reply_mode TEXT NOT NULL,
            uzbek_beta_notice_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        INSERT INTO user_settings (
            telegram_user_id,
            source_language,
            target_language,
            reply_mode,
            uzbek_beta_notice_enabled
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (42, "auto", "ru", "text_only", 1),
    )
    connection.commit()
    connection.close()

    database = Database(database_path)
    database.initialize()
    repository = UserSettingsRepository(database)

    settings = repository.get_by_user_id(42)

    assert settings is not None
    assert settings.source_language is LanguageCode.RU
