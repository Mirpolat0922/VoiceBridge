from pydantic import BaseModel, ConfigDict

from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode


class UserSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    telegram_user_id: int
    source_language: LanguageCode
    target_language: LanguageCode
    reply_mode: ReplyMode
    uzbek_beta_notice_enabled: bool = True
