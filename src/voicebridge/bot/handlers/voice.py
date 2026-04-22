import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.types import FSInputFile, Message, ReplyParameters

from voicebridge.domain.languages import LanguageCode
from voicebridge.domain.reply_modes import ReplyMode
from voicebridge.services.asr import AsrError, AsrService
from voicebridge.services.audio import AudioProcessingError, AudioService
from voicebridge.services.pipeline.text_pipeline import GroqTextPipeline, GroqTextPipelineError
from voicebridge.services.tts import TtsError, TtsService
from voicebridge.services.user_settings import UserSettingsService

router = Router()


def _language_summary(source_language: LanguageCode, target_language: LanguageCode) -> str:
    return (
        f"{source_language.label} ({source_language.value.upper()}) -> "
        f"{target_language.label} ({target_language.value.upper()})"
    )


async def _cleanup_request_temporary_files(
    *,
    audio_service: AudioService,
    normalized_audio,
    tts_service: TtsService,
    synthesized_speech,
    logger: logging.Logger,
) -> None:
    if normalized_audio is not None:
        try:
            await asyncio.to_thread(audio_service.cleanup_temporary_files, normalized_audio)
        except AudioProcessingError:
            logger.warning(
                "Temporary audio cleanup failed",
                extra={
                    "source_path": str(normalized_audio.source_path),
                    "normalized_path": str(normalized_audio.normalized_path),
                },
            )
    if synthesized_speech is not None:
        try:
            await asyncio.to_thread(tts_service.cleanup_temporary_files, synthesized_speech)
        except OSError:
            logger.warning(
                "Temporary TTS cleanup failed",
                extra={"voice_path": str(synthesized_speech.voice_path)},
            )


@router.message(F.voice)
async def handle_voice_message(
    message: Message,
    bot: Bot,
    audio_service: AudioService,
    asr_service: AsrService,
    tts_service: TtsService,
    groq_text_pipeline: GroqTextPipeline,
    user_settings_service: UserSettingsService,
) -> None:
    logger = logging.getLogger(__name__)

    if message.voice is None:
        await message.answer("I expected a Telegram voice message.")
        return
    if message.from_user is None:
        await message.answer("I could not identify the Telegram user for this message.")
        return

    user_settings = user_settings_service.get_or_create(message.from_user.id)
    requested_language = user_settings.source_language
    target_language = user_settings.target_language
    total_stages = 5 if user_settings.reply_mode is ReplyMode.TEXT_AND_VOICE else 4
    progress_message = await message.answer(
        f"VoiceBridge is processing this voice note.\nStage 1/{total_stages}: downloading audio",
        reply_parameters=ReplyParameters(message_id=message.message_id),
    )
    normalized_audio = None
    synthesized_speech = None

    try:
        downloaded_audio = await audio_service.download_voice(bot, message.voice)
        await progress_message.edit_text(
            f"VoiceBridge is processing this voice note.\nStage 2/{total_stages}: normalizing audio"
        )
        normalized_audio = await asyncio.to_thread(audio_service.normalize, downloaded_audio)
        await progress_message.edit_text(
            "VoiceBridge is processing this voice note.\n"
            f"Stage 3/{total_stages}: transcribing speech"
        )
        transcription = await asyncio.to_thread(
            asr_service.transcribe,
            normalized_audio,
            requested_language=requested_language,
        )
        await progress_message.edit_text(
            f"VoiceBridge is processing this voice note.\nStage 4/{total_stages}: translating text"
        )
        pipeline_result = await asyncio.to_thread(
            groq_text_pipeline.process,
            transcription.text,
            source_language=requested_language,
            target_language=target_language,
        )
        if user_settings.reply_mode is ReplyMode.TEXT_AND_VOICE:
            await progress_message.edit_text(
                "VoiceBridge is processing this voice note.\n"
                f"Stage 5/{total_stages}: generating translated speech"
            )
            try:
                synthesized_speech = await asyncio.to_thread(
                    tts_service.synthesize,
                    pipeline_result.translated_text,
                    language=target_language,
                )
            except TtsError as error:
                logger.exception("Speech synthesis failed: %s", error)
                synthesized_speech = None
    except AudioProcessingError as error:
        logger.exception("Audio processing failed: %s", error)
        await message.answer("I could not process that voice message yet.")
    except AsrError as error:
        logger.exception("Speech recognition failed: %s", error)
        await progress_message.edit_text("I could not transcribe that voice message yet.")
    except GroqTextPipelineError as error:
        logger.exception("Text pipeline failed: %s", error)
        error_text = str(error)
        await progress_message.edit_text(error_text)
    else:
        logger.info(
            "Voice message transcribed",
            extra={
                "original_path": str(downloaded_audio.original_path),
                "normalized_path": str(normalized_audio.normalized_path),
                "requested_language": requested_language.value,
                "detected_language": (
                    transcription.detected_language.value
                    if transcription.detected_language
                    else None
                ),
                "provider_name": transcription.provider_name,
                "text_pipeline_provider_name": pipeline_result.provider_name,
                "target_language": target_language.value,
                "tts_provider_name": (
                    synthesized_speech.provider_name if synthesized_speech is not None else None
                ),
            },
        )

        uzbek_notice = ""
        if (
            requested_language is LanguageCode.UZ
            or transcription.detected_language is LanguageCode.UZ
        ) and user_settings.uzbek_beta_notice_enabled:
            uzbek_notice = "\nUzbek transcription is currently in beta mode."
        voice_notice = ""
        if user_settings.reply_mode is ReplyMode.TEXT_AND_VOICE and synthesized_speech is None:
            voice_notice = "\n\nTranslated voice reply was unavailable for this request."

        await progress_message.edit_text(
            "VoiceBridge Result\n\n"
            f"🌐 Languages: {_language_summary(requested_language, target_language)}\n"
            f"🔊 Reply mode: {user_settings.reply_mode.label}\n\n"
            "📝 Transcript\n"
            f"{transcription.text}\n\n"
            "🌍 Translated message\n"
            f"{pipeline_result.translated_text}"
            f"{voice_notice}"
            f"{uzbek_notice}\n\n"
            "⚙️ Settings are global. Use /settings any time to change source, target, "
            "or reply mode.",
        )

        if synthesized_speech is not None:
            try:
                await message.answer_voice(
                    voice=FSInputFile(synthesized_speech.voice_path),
                    reply_parameters=ReplyParameters(message_id=message.message_id),
                )
            except Exception:
                logger.warning(
                    "Translated voice delivery failed",
                    extra={"voice_path": str(synthesized_speech.voice_path)},
                )
    finally:
        await _cleanup_request_temporary_files(
            audio_service=audio_service,
            normalized_audio=normalized_audio,
            tts_service=tts_service,
            synthesized_speech=synthesized_speech,
            logger=logger,
        )
