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
    return _build_keyboard(settings, surface="panel", section=section)


def build_result_keyboard(
    settings: UserSettings,
    *,
    section: str = "main",
) -> InlineKeyboardMarkup:
    return _build_keyboard(settings, surface="result", section=section)


def _build_keyboard(
    settings: UserSettings,
    *,
    surface: str,
    section: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if section == "main":
        builder.button(
            text=f"Source {settings.source_language.value.upper()} >",
            callback_data=f"ui:{surface}:open:source",
        )
        builder.button(
            text=f"Target {settings.target_language.value.upper()} >",
            callback_data=f"ui:{surface}:open:target",
        )
        builder.button(
            text=f"Reply {settings.reply_mode.label} >",
            callback_data=f"ui:{surface}:open:reply",
        )
        if surface == "result":
            builder.button(
                text="Open Control Center",
                callback_data="ui:result:open_panel",
            )
            builder.adjust(2, 1, 1)
        else:
            builder.adjust(2, 1)
        return builder.as_markup()

    if section == "source":
        for language in LanguageCode.selectable_sources():
            prefix = "● " if settings.source_language is language else ""
            label = f"{prefix}{language.value.upper()}"
            builder.button(text=label, callback_data=f"ui:{surface}:set_source:{language.value}")
        builder.button(text="< Back", callback_data=f"ui:{surface}:back")
        builder.adjust(2, 2, 1)
        return builder.as_markup()

    if section == "target":
        for language in LanguageCode.supported():
            prefix = "● " if settings.target_language is language else ""
            label = f"{prefix}{language.value.upper()}"
            builder.button(text=label, callback_data=f"ui:{surface}:set_target:{language.value}")
        builder.button(text="< Back", callback_data=f"ui:{surface}:back")
        builder.adjust(2, 1, 1)
        return builder.as_markup()

    if section == "reply":
        for reply_mode in ReplyMode:
            label = f"{'● ' if settings.reply_mode is reply_mode else ''}{reply_mode.label}"
            builder.button(
                text=label,
                callback_data=f"ui:{surface}:set_reply:{reply_mode.value}",
            )
        builder.button(text="< Back", callback_data=f"ui:{surface}:back")
        builder.adjust(1, 1, 1)
        return builder.as_markup()

    return _build_keyboard(settings, surface=surface, section="main")
