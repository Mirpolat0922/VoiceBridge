import asyncio
import logging

from aiogram import Bot, Dispatcher

from voicebridge.bot.handlers.settings import router as settings_router
from voicebridge.bot.handlers.start import router as start_router
from voicebridge.bot.handlers.voice import router as voice_router
from voicebridge.config import get_settings
from voicebridge.services.asr import (
    AsrProviderRegistry,
    AsrRouter,
    AsrService,
    FasterWhisperAsrProvider,
    NemoUzbekAsrProvider,
)
from voicebridge.services.audio import AudioService
from voicebridge.services.pipeline.text_pipeline import GroqTextPipeline
from voicebridge.services.tts import GttsProvider, TtsProviderRegistry, TtsService
from voicebridge.services.user_settings import UserSettingsService
from voicebridge.storage.database import Database
from voicebridge.storage.user_settings_repository import UserSettingsRepository
from voicebridge.utils.logging import configure_logging
from voicebridge.utils.runtime import configure_runtime_environment


def build_dispatcher(
    user_settings_service: UserSettingsService,
    audio_service: AudioService,
    asr_service: AsrService,
    tts_service: TtsService,
    groq_text_pipeline: GroqTextPipeline,
) -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher["user_settings_service"] = user_settings_service
    dispatcher["audio_service"] = audio_service
    dispatcher["asr_service"] = asr_service
    dispatcher["tts_service"] = tts_service
    dispatcher["groq_text_pipeline"] = groq_text_pipeline
    dispatcher.include_router(start_router)
    dispatcher.include_router(settings_router)
    dispatcher.include_router(voice_router)
    return dispatcher


async def _run_polling() -> None:
    settings = get_settings()

    configure_logging(settings.log_level)
    configure_runtime_environment(settings.storage_dir)
    logger = logging.getLogger(__name__)

    database = Database(settings.db_path)
    database.initialize()

    user_settings_repository = UserSettingsRepository(database)
    user_settings_service = UserSettingsService(
        repository=user_settings_repository,
        default_source_language=settings.default_source_language,
        default_target_language=settings.default_target_language,
        default_reply_mode=settings.default_reply_mode,
    )
    audio_service = AudioService(settings.storage_dir)
    asr_registry = AsrProviderRegistry(
        providers=[
            FasterWhisperAsrProvider(
                model_size=settings.whisper_model_size,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            ),
            NemoUzbekAsrProvider(
                model_name=settings.nemo_uzbek_model_name,
            ),
        ]
    )
    asr_router = AsrRouter(
        uz_provider=settings.asr_provider_uz,
        ru_provider=settings.asr_provider_ru,
        en_provider=settings.asr_provider_en,
    )
    asr_service = AsrService(registry=asr_registry, router=asr_router)
    tts_registry = TtsProviderRegistry(
        providers=[
            GttsProvider(
                storage_dir=settings.storage_dir,
            ),
        ]
    )
    tts_service = TtsService(
        registry=tts_registry,
        default_provider_name="gtts",
    )
    groq_text_pipeline = GroqTextPipeline(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model_name,
        endpoint=settings.groq_endpoint,
        max_attempts=settings.groq_max_attempts,
        retry_base_delay_seconds=settings.groq_retry_base_delay_seconds,
        max_completion_tokens=settings.groq_max_completion_tokens,
    )

    bot = Bot(token=settings.bot_token)
    dispatcher = build_dispatcher(
        user_settings_service,
        audio_service,
        asr_service,
        tts_service,
        groq_text_pipeline,
    )

    logger.info("Starting VoiceBridge bot polling")
    await dispatcher.start_polling(bot)


def run_polling() -> None:
    asyncio.run(_run_polling())
