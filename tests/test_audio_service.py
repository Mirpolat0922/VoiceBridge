import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from voicebridge.schemas.audio import DownloadedAudio, NormalizedAudio
from voicebridge.services.audio import AudioProcessingError, AudioService


def test_audio_service_creates_directories(tmp_path: Path) -> None:
    AudioService(tmp_path / "audio")

    assert (tmp_path / "audio" / "incoming").exists()
    assert (tmp_path / "audio" / "normalized").exists()


def test_normalize_builds_expected_output_path(tmp_path: Path) -> None:
    service = AudioService(tmp_path / "audio")
    original_path = tmp_path / "audio" / "incoming" / "sample.ogg"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(b"placeholder")

    downloaded_audio = DownloadedAudio(
        telegram_file_id="voice-id",
        original_path=original_path,
        original_format="ogg",
        duration_seconds=3,
    )

    with patch("voicebridge.services.audio.service.subprocess.run") as mocked_run:
        mocked_run.return_value = Mock(returncode=0)
        normalized_audio = service.normalize(downloaded_audio)

    mocked_run.assert_called_once()
    assert normalized_audio.normalized_path == tmp_path / "audio" / "normalized" / "sample.wav"
    assert normalized_audio.sample_rate_hz == 16_000
    assert normalized_audio.channels == 1


def test_cleanup_temporary_files_removes_source_and_normalized_files(tmp_path: Path) -> None:
    service = AudioService(tmp_path / "audio")
    original_path = tmp_path / "audio" / "incoming" / "sample.ogg"
    normalized_path = tmp_path / "audio" / "normalized" / "sample.wav"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(b"source")
    normalized_path.write_bytes(b"normalized")

    normalized_audio = NormalizedAudio(
        telegram_file_id="voice-id",
        source_path=original_path,
        normalized_path=normalized_path,
        sample_rate_hz=16_000,
        channels=1,
    )

    service.cleanup_temporary_files(normalized_audio)

    assert not original_path.exists()
    assert not normalized_path.exists()


def test_normalize_raises_audio_processing_error_on_ffmpeg_failure(tmp_path: Path) -> None:
    service = AudioService(tmp_path / "audio")
    original_path = tmp_path / "audio" / "incoming" / "broken.ogg"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(b"placeholder")

    downloaded_audio = DownloadedAudio(
        telegram_file_id="voice-id",
        original_path=original_path,
        original_format="ogg",
    )

    with patch("voicebridge.services.audio.service.subprocess.run") as mocked_run:
        mocked_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["ffmpeg"],
            stderr="bad input",
        )

        with pytest.raises(AudioProcessingError, match="Failed to normalize audio"):
            service.normalize(downloaded_audio)
