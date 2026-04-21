from abc import ABC, abstractmethod

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.audio import NormalizedAudio
from voicebridge.schemas.transcription import TranscriptionResult


class AsrProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def transcribe(
        self,
        audio: NormalizedAudio,
        *,
        requested_language: LanguageCode,
    ) -> TranscriptionResult:
        raise NotImplementedError
