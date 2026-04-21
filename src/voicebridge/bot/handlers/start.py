from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from voicebridge.bot.ui.settings_keyboard import build_control_center_keyboard
from voicebridge.services.user_settings import UserSettingsService

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, user_settings_service: UserSettingsService) -> None:
    user = message.from_user
    if user is None:
        await message.answer("VoiceBridge is ready.")
        return

    settings = user_settings_service.get_or_create(user.id)
    text = (
        "VoiceBridge Control Center\n\n"
        "Send a voice message in Uzbek, Russian, or English and VoiceBridge will return:\n"
        "- transcript\n"
        "- cleaned transcript\n"
        "- translation\n"
        "- optional translated voice reply\n\n"
        f"Current source: {settings.source_language.value.upper()}\n"
        f"Current target: {settings.target_language.value.upper()}\n"
        f"Current reply mode: {settings.reply_mode.label}\n\n"
        "Use the buttons below to open Source, Target, or Reply mode menus.\n\n"
        "Uzbek is available in beta while the speech pipeline is still being tuned."
    )
    await message.answer(text, reply_markup=build_control_center_keyboard(settings))
