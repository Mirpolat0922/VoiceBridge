import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from voicebridge.schemas.audio import DownloadedAudio, NormalizedAudio
from voicebridge.services.audio.exceptions import AudioProcessingError

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Voice


class AudioService:
    def __init__(
        self,
        storage_dir: Path,
        *,
        sample_rate_hz: int = 16_000,
        channels: int = 1,
    ) -> None:
        self._storage_dir = storage_dir
        self._incoming_dir = storage_dir / "incoming"
        self._normalized_dir = storage_dir / "normalized"
        self._sample_rate_hz = sample_rate_hz
        self._channels = channels

        self._incoming_dir.mkdir(parents=True, exist_ok=True)
        self._normalized_dir.mkdir(parents=True, exist_ok=True)

    async def download_voice(self, bot: "Bot", voice: "Voice") -> DownloadedAudio:
        original_path = self._incoming_dir / f"{voice.file_unique_id}.ogg"

        try:
            telegram_file = await bot.get_file(voice.file_id)
            await bot.download_file(telegram_file.file_path, destination=original_path)
        except Exception as error:  # pragma: no cover - defensive boundary around Telegram I/O
            raise AudioProcessingError("Failed to download Telegram voice message.") from error

        return DownloadedAudio(
            telegram_file_id=voice.file_id,
            original_path=original_path,
            original_format="ogg",
            duration_seconds=voice.duration,
        )

    def normalize(self, downloaded_audio: DownloadedAudio) -> NormalizedAudio:
        normalized_path = self._normalized_dir / f"{downloaded_audio.original_path.stem}.wav"

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(downloaded_audio.original_path),
            "-ac",
            str(self._channels),
            "-ar",
            str(self._sample_rate_hz),
            str(normalized_path),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            raise AudioProcessingError(
                f"Failed to normalize audio with ffmpeg: {error.stderr.strip()}"
            ) from error

        return NormalizedAudio(
            telegram_file_id=downloaded_audio.telegram_file_id,
            source_path=downloaded_audio.original_path,
            normalized_path=normalized_path,
            sample_rate_hz=self._sample_rate_hz,
            channels=self._channels,
        )

    def cleanup_temporary_files(self, normalized_audio: NormalizedAudio) -> None:
        for path in (normalized_audio.source_path, normalized_audio.normalized_path):
            try:
                path.unlink(missing_ok=True)
            except OSError as error:
                raise AudioProcessingError(
                    f"Failed to clean up temporary audio file '{path}'."
                ) from error
