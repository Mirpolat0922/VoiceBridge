from pathlib import Path

import pytest

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.audio import NormalizedAudio
from voicebridge.schemas.transcription import TranscriptionResult
from voicebridge.services.asr import (
    AsrError,
    AsrProvider,
    AsrProviderRegistry,
    AsrRouter,
    AsrService,
)


class FakeAsrProvider(AsrProvider):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def transcribe(
        self,
        audio: NormalizedAudio,
        *,
        requested_language: LanguageCode,
    ) -> TranscriptionResult:
        return TranscriptionResult(
            text=f"{self._name}:{requested_language.value}",
            provider_name=self._name,
            audio_path=audio.normalized_path,
            requested_language=requested_language,
            detected_language=requested_language,
        )


def build_audio() -> NormalizedAudio:
    return NormalizedAudio(
        telegram_file_id="voice-id",
        source_path=Path("/tmp/source.ogg"),
        normalized_path=Path("/tmp/normalized.wav"),
        sample_rate_hz=16_000,
        channels=1,
    )


def test_router_resolves_provider_by_language() -> None:
    router = AsrRouter(
        uz_provider="uzbek-specialist",
        ru_provider="whisper-ru",
        en_provider="whisper-en",
    )

    assert router.resolve_provider_name(LanguageCode.UZ) == "uzbek-specialist"
    assert router.resolve_provider_name(LanguageCode.RU) == "whisper-ru"
    assert router.resolve_provider_name(LanguageCode.EN) == "whisper-en"


def test_service_uses_routed_provider() -> None:
    registry = AsrProviderRegistry(
        providers=[FakeAsrProvider("whisper-shared"), FakeAsrProvider("uzbek-specialist")]
    )
    router = AsrRouter(
        uz_provider="uzbek-specialist",
        ru_provider="whisper-shared",
        en_provider="whisper-shared",
    )
    service = AsrService(registry=registry, router=router)

    result = service.transcribe(build_audio(), requested_language=LanguageCode.UZ)

    assert result.provider_name == "uzbek-specialist"
    assert result.text == "uzbek-specialist:uz"


def test_registry_raises_for_unknown_provider() -> None:
    registry = AsrProviderRegistry(providers=[FakeAsrProvider("known")])

    with pytest.raises(AsrError, match="Unknown ASR provider"):
        registry.get("missing")


def test_service_routes_whisper_for_ru_and_nemo_for_uz() -> None:
    registry = AsrProviderRegistry(
        providers=[FakeAsrProvider("faster_whisper"), FakeAsrProvider("nemo_uzbek")]
    )
    router = AsrRouter(
        uz_provider="nemo_uzbek",
        ru_provider="faster_whisper",
        en_provider="faster_whisper",
    )
    service = AsrService(registry=registry, router=router)
    audio = build_audio()

    ru_result = service.transcribe(audio, requested_language=LanguageCode.RU)
    uz_result = service.transcribe(audio, requested_language=LanguageCode.UZ)

    assert ru_result.provider_name == "faster_whisper"
    assert uz_result.provider_name == "nemo_uzbek"
