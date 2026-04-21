from pathlib import Path

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.tts import SynthesizedSpeechResult
from voicebridge.services.tts import TtsError, TtsProvider, TtsProviderRegistry, TtsService


class FakeTtsProvider(TtsProvider):
    @property
    def name(self) -> str:
        return "fake"

    def synthesize(
        self,
        text: str,
        *,
        language: LanguageCode,
    ) -> SynthesizedSpeechResult:
        return SynthesizedSpeechResult(
            provider_name=self.name,
            language=language,
            source_text=text,
            voice_path=Path("/tmp/fake.ogg"),
            temporary_paths=(Path("/tmp/fake.ogg"),),
        )


def test_tts_service_uses_default_provider() -> None:
    service = TtsService(
        registry=TtsProviderRegistry(providers=[FakeTtsProvider()]),
        default_provider_name="fake",
    )

    result = service.synthesize("hello", language=LanguageCode.EN)

    assert result.provider_name == "fake"
    assert result.language is LanguageCode.EN
    assert result.source_text == "hello"


def test_tts_registry_raises_for_unknown_provider() -> None:
    registry = TtsProviderRegistry(providers=[FakeTtsProvider()])

    try:
        registry.get("missing")
    except TtsError as error:
        assert "Unknown TTS provider" in str(error)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("Expected TtsError for unknown provider")


def test_tts_service_cleanup_removes_temporary_files(tmp_path: Path) -> None:
    voice_path = tmp_path / "tts.ogg"
    voice_path.write_bytes(b"voice")

    service = TtsService(
        registry=TtsProviderRegistry(providers=[FakeTtsProvider()]),
        default_provider_name="fake",
    )
    result = SynthesizedSpeechResult(
        provider_name="fake",
        language=LanguageCode.EN,
        source_text="hello",
        voice_path=voice_path,
        temporary_paths=(voice_path,),
    )

    service.cleanup_temporary_files(result)

    assert not voice_path.exists()
