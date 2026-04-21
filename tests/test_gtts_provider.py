import types
from pathlib import Path

import pytest

from voicebridge.domain.languages import LanguageCode
from voicebridge.services.tts.providers.gtts_provider import GttsProvider


class FakeGttsClient:
    def __init__(self, *, text: str, lang: str) -> None:
        self._text = text
        self._lang = lang

    def save(self, path: str) -> None:
        Path(path).write_bytes(f"{self._lang}:{self._text}".encode("utf-8"))


def test_gtts_provider_synthesizes_and_converts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider = GttsProvider(storage_dir=tmp_path)

    fake_module = types.SimpleNamespace(gTTS=FakeGttsClient)
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "gtts":
            return fake_module
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    def fake_run(command, check, capture_output, text):
        output_path = Path(command[-1])
        output_path.write_bytes(b"ogg-data")
        return None

    monkeypatch.setattr(
        "voicebridge.services.tts.providers.gtts_provider.subprocess.run",
        fake_run,
    )

    result = provider.synthesize("Hello world", language=LanguageCode.EN)

    assert result.provider_name == "gtts"
    assert result.voice_path.read_bytes() == b"ogg-data"
