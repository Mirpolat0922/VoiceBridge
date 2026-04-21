from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.schemas.user_settings import UserSettings
from voicebridge.storage.database import Database


class UserSettingsRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def get_by_user_id(self, telegram_user_id: int) -> UserSettings | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    telegram_user_id,
                    source_language,
                    target_language,
                    reply_mode,
                    uzbek_beta_notice_enabled
                FROM user_settings
                WHERE telegram_user_id = ?
                """,
                (telegram_user_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_model(row)

    def upsert(self, settings: UserSettings) -> UserSettings:
        with self._database.connect() as connection:
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
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    source_language = excluded.source_language,
                    target_language = excluded.target_language,
                    reply_mode = excluded.reply_mode,
                    uzbek_beta_notice_enabled = excluded.uzbek_beta_notice_enabled,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    settings.telegram_user_id,
                    settings.source_language.value,
                    settings.target_language.value,
                    settings.reply_mode.value,
                    int(settings.uzbek_beta_notice_enabled),
                ),
            )

        saved_settings = self.get_by_user_id(settings.telegram_user_id)
        if saved_settings is None:
            raise RuntimeError("User settings were not persisted correctly.")

        return saved_settings

    @staticmethod
    def _row_to_model(row: object) -> UserSettings:
        return UserSettings(
            telegram_user_id=row["telegram_user_id"],
            source_language=LanguageCode(row["source_language"]),
            target_language=LanguageCode(row["target_language"]),
            reply_mode=ReplyMode(row["reply_mode"]),
            uzbek_beta_notice_enabled=bool(row["uzbek_beta_notice_enabled"]),
        )
