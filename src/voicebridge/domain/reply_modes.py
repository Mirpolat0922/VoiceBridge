from enum import StrEnum


class ReplyMode(StrEnum):
    TEXT_ONLY = "text_only"
    TEXT_AND_VOICE = "text_and_voice"

    @property
    def label(self) -> str:
        if self is ReplyMode.TEXT_ONLY:
            return "Text only"
        return "Text + voice"
