from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from voicebridge.bot.ui.settings_keyboard import (
    build_control_center_keyboard,
    build_result_keyboard,
)
from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.schemas.user_settings import UserSettings
from voicebridge.services.user_settings import UserSettingsService

router = Router()


def _format_settings_text(
    source_language: LanguageCode,
    target_language: LanguageCode,
    reply_mode: ReplyMode,
    *,
    section: str = "main",
) -> str:
    section_help = {
        "main": "Choose what you want to change.",
        "source": "Select the language you usually speak in your next voice message.",
        "target": "Select the language you want VoiceBridge to translate into.",
        "reply": "Choose whether the bot should send text only or text plus voice.",
    }
    return (
        "VoiceBridge Control Center\n\n"
        "Current configuration\n"
        f"Source: {source_language.value.upper()}\n"
        f"Target: {target_language.value.upper()}\n"
        f"Reply mode: {reply_mode.label}\n\n"
        f"{section_help.get(section, section_help['main'])}\n\n"
        "Quick commands\n"
        "/source auto|uz|ru|en\n"
        "/target uz|ru|en\n"
        "/reply text_only|text_and_voice\n"
        "/settings\n\n"
        "Tip: You can change settings from result messages without losing previous results."
    )


def _is_control_panel_message(text: str | None) -> bool:
    if not text:
        return False
    return text.startswith("VoiceBridge Control Center")


async def _refresh_message_for_settings(
    callback_query: CallbackQuery,
    settings: UserSettings,
    *,
    section: str = "main",
) -> None:
    if callback_query.message is None:
        return

    if _is_control_panel_message(callback_query.message.text):
        await callback_query.message.edit_text(
            _format_settings_text(
                settings.source_language,
                settings.target_language,
                settings.reply_mode,
                section=section,
            ),
            reply_markup=build_control_center_keyboard(settings, section=section),
        )
        return

    await callback_query.message.edit_reply_markup(
        reply_markup=build_result_keyboard(settings, section=section),
    )


@router.message(Command("settings"))
async def handle_settings(message: Message, user_settings_service: UserSettingsService) -> None:
    if message.from_user is None:
        await message.answer("I could not identify the Telegram user for this message.")
        return

    settings = user_settings_service.get_or_create(message.from_user.id)
    await message.answer(
        _format_settings_text(
            settings.source_language,
            settings.target_language,
            settings.reply_mode,
        ),
        reply_markup=build_control_center_keyboard(settings),
    )


@router.message(Command("source"))
async def handle_source_command(
    message: Message,
    command: CommandObject,
    user_settings_service: UserSettingsService,
) -> None:
    if message.from_user is None:
        await message.answer("I could not identify the Telegram user for this message.")
        return

    raw_language = (command.args or "").strip().lower()
    if not raw_language:
        available = ", ".join(language.value for language in LanguageCode.selectable_sources())
        await message.answer(
            "Please provide a source language.\n\n"
            f"Example: /source uz\nAvailable: {available}"
        )
        return

    try:
        source_language = LanguageCode(raw_language)
    except ValueError:
        available = ", ".join(language.value for language in LanguageCode.selectable_sources())
        await message.answer(f"Unsupported source language. Available: {available}")
        return

    if source_language not in LanguageCode.selectable_sources():
        available = ", ".join(language.value for language in LanguageCode.selectable_sources())
        await message.answer(f"Unsupported source language. Available: {available}")
        return

    settings = user_settings_service.update(
        message.from_user.id,
        source_language=source_language,
    )

    await message.answer(
        "Source language updated.\n\n"
        f"New source language: {settings.source_language.value.upper()}\n"
        "Use /settings to review your current configuration.",
        reply_markup=build_control_center_keyboard(settings),
    )


@router.message(Command("target"))
async def handle_target_command(
    message: Message,
    command: CommandObject,
    user_settings_service: UserSettingsService,
) -> None:
    if message.from_user is None:
        await message.answer("I could not identify the Telegram user for this message.")
        return

    raw_language = (command.args or "").strip().lower()
    if not raw_language:
        available = ", ".join(language.value for language in LanguageCode.supported())
        await message.answer(
            "Please provide a target language.\n\n"
            f"Example: /target ru\nAvailable: {available}"
        )
        return

    try:
        target_language = LanguageCode(raw_language)
    except ValueError:
        available = ", ".join(language.value for language in LanguageCode.supported())
        await message.answer(f"Unsupported target language. Available: {available}")
        return

    if target_language not in LanguageCode.supported():
        available = ", ".join(language.value for language in LanguageCode.supported())
        await message.answer(f"Unsupported target language. Available: {available}")
        return

    settings = user_settings_service.update(
        message.from_user.id,
        target_language=target_language,
    )

    await message.answer(
        "Target language updated.\n\n"
        f"New target language: {settings.target_language.value.upper()}\n"
        "Use /settings to review your current configuration.",
        reply_markup=build_control_center_keyboard(settings),
    )


@router.message(Command("reply"))
async def handle_reply_command(
    message: Message,
    command: CommandObject,
    user_settings_service: UserSettingsService,
) -> None:
    if message.from_user is None:
        await message.answer("I could not identify the Telegram user for this message.")
        return

    raw_reply_mode = (command.args or "").strip().lower()
    if not raw_reply_mode:
        available = ", ".join(reply_mode.value for reply_mode in ReplyMode)
        await message.answer(
            "Please provide a reply mode.\n\n"
            f"Example: /reply text_and_voice\nAvailable: {available}"
        )
        return

    try:
        reply_mode = ReplyMode(raw_reply_mode)
    except ValueError:
        available = ", ".join(reply_mode.value for reply_mode in ReplyMode)
        await message.answer(f"Unsupported reply mode. Available: {available}")
        return

    settings = user_settings_service.update(
        message.from_user.id,
        reply_mode=reply_mode,
    )

    await message.answer(
        "Reply mode updated.\n\n"
        f"New reply mode: {settings.reply_mode.label}\n"
        "Use /settings to review your current configuration.",
        reply_markup=build_control_center_keyboard(settings),
    )


@router.callback_query(F.data.startswith("ui:"))
async def handle_ui_callback(
    callback_query: CallbackQuery,
    user_settings_service: UserSettingsService,
) -> None:
    if (
        callback_query.from_user is None
        or callback_query.message is None
        or callback_query.data is None
    ):
        await callback_query.answer()
        return

    parts = callback_query.data.split(":")
    if len(parts) < 3:
        await callback_query.answer()
        return

    _, surface, action, *rest = parts
    settings = user_settings_service.get_or_create(callback_query.from_user.id)

    if action == "open":
        section = rest[0]
        await _refresh_message_for_settings(callback_query, settings, section=section)
        await callback_query.answer()
        return

    if action == "back":
        await _refresh_message_for_settings(callback_query, settings, section="main")
        await callback_query.answer()
        return

    if surface == "result" and action == "open_panel":
        await callback_query.message.answer(
            _format_settings_text(
                settings.source_language,
                settings.target_language,
                settings.reply_mode,
            ),
            reply_markup=build_control_center_keyboard(settings),
        )
        await callback_query.answer("Control center opened.")
        return

    if action == "set_source":
        source_language = LanguageCode(rest[0])
        if settings.source_language is source_language:
            await callback_query.answer("Source language is already selected.")
            return
        settings = user_settings_service.update(
            callback_query.from_user.id,
            source_language=source_language,
        )
        await _refresh_message_for_settings(callback_query, settings, section="source")
        await callback_query.answer("Source language updated.")
        return

    if action == "set_target":
        target_language = LanguageCode(rest[0])
        if settings.target_language is target_language:
            await callback_query.answer("Target language is already selected.")
            return
        settings = user_settings_service.update(
            callback_query.from_user.id,
            target_language=target_language,
        )
        await _refresh_message_for_settings(callback_query, settings, section="target")
        await callback_query.answer("Target language updated.")
        return

    if action == "set_reply":
        reply_mode = ReplyMode(rest[0])
        if settings.reply_mode is reply_mode:
            await callback_query.answer("Reply mode is already selected.")
            return
        settings = user_settings_service.update(
            callback_query.from_user.id,
            reply_mode=reply_mode,
        )
        await _refresh_message_for_settings(callback_query, settings, section="reply")
        await callback_query.answer("Reply mode updated.")
        return

    await callback_query.answer()
