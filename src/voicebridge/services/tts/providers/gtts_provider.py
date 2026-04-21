import subprocess
from pathlib import Path
from uuid import uuid4

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.tts import SynthesizedSpeechResult
from voicebridge.services.tts.base import TtsProvider
from voicebridge.services.tts.exceptions import TtsError


class GttsProvider(TtsProvider):
    _LANGUAGE_BY_CODE = {
        LanguageCode.EN: "en",
        LanguageCode.RU: "ru",
        LanguageCode.UZ: "uz",
    }

    def __init__(self, *, storage_dir: Path) -> None:
        self._storage_dir = storage_dir / "tts"
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "gtts"

    def synthesize(
        self,
        text: str,
        *,
        language: LanguageCode,
    ) -> SynthesizedSpeechResult:
        if language not in LanguageCode.supported():
            raise TtsError(f"Unsupported TTS language '{language.value}'.")
        if not text.strip():
            raise TtsError("Cannot synthesize empty text.")

        gtts_language = self._LANGUAGE_BY_CODE.get(language)
        if gtts_language is None:
            raise TtsError(f"No gTTS language is configured for '{language.value}'.")

        try:
            from gtts import gTTS
        except ImportError as error:  # pragma: no cover - runtime dependency boundary
            raise TtsError(
                "gTTS is not installed. Reinstall project dependencies to use TTS."
            ) from error

        stem = uuid4().hex
        mp3_path = self._storage_dir / f"{stem}.mp3"
        ogg_path = self._storage_dir / f"{stem}.ogg"

        try:
            gTTS(text=text, lang=gtts_language).save(str(mp3_path))
        except Exception as error:  # pragma: no cover - external API boundary
            raise TtsError("gTTS synthesis failed.") from error

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_path),
            "-c:a",
            "libopus",
            "-b:a",
            "48k",
            str(ogg_path),
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            raise TtsError(
                f"Failed to convert synthesized speech with ffmpeg: {error.stderr.strip()}"
            ) from error

        return SynthesizedSpeechResult(
            provider_name=self.name,
            language=language,
            source_text=text,
            voice_path=ogg_path,
            temporary_paths=(mp3_path, ogg_path),
        )
