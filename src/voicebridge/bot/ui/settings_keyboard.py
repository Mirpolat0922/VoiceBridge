from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.schemas.user_settings import UserSettings


def build_control_center_keyboard(
    settings: UserSettings,
    *,
    section: str = "main",
) -> InlineKeyboardMarkup:
    return _build_keyboard(settings, section=section)


def _build_keyboard(
    settings: UserSettings,
    *,
    section: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if section == "main":
        builder.button(
            text=f"🗣 Source: {settings.source_language.label}",
            callback_data="ui:panel:open:source",
        )
        builder.button(
            text=f"🎯 Target: {settings.target_language.label}",
            callback_data="ui:panel:open:target",
        )
        builder.button(
            text=f"🔊 Reply: {settings.reply_mode.label}",
            callback_data="ui:panel:open:reply",
        )
        builder.adjust(1, 1, 1)
        return builder.as_markup()

    if section == "source":
        for language in LanguageCode.selectable_sources():
            prefix = "✓ " if settings.source_language is language else ""
            builder.button(
                text=f"{prefix}{language.label}",
                callback_data=f"ui:panel:set_source:{language.value}",
            )
        builder.button(text="← Back", callback_data="ui:panel:back")
        builder.adjust(1, 1, 1, 1)
        return builder.as_markup()

    if section == "target":
        for language in LanguageCode.supported():
            prefix = "✓ " if settings.target_language is language else ""
            builder.button(
                text=f"{prefix}{language.label}",
                callback_data=f"ui:panel:set_target:{language.value}",
            )
        builder.button(text="← Back", callback_data="ui:panel:back")
        builder.adjust(1, 1, 1, 1)
        return builder.as_markup()

    if section == "reply":
        for reply_mode in ReplyMode:
            label = f"{'✓ ' if settings.reply_mode is reply_mode else ''}{reply_mode.label}"
            builder.button(
                text=label,
                callback_data=f"ui:panel:set_reply:{reply_mode.value}",
            )
        builder.button(text="← Back", callback_data="ui:panel:back")
        builder.adjust(1, 1, 1)
        return builder.as_markup()

    return _build_keyboard(settings, section="main")
