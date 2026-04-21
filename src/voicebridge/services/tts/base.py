from abc import ABC, abstractmethod

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.tts import SynthesizedSpeechResult


class TtsProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def synthesize(
        self,
        text: str,
        *,
        language: LanguageCode,
    ) -> SynthesizedSpeechResult:
        raise NotImplementedError
