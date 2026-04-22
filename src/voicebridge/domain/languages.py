from enum import StrEnum


class LanguageCode(StrEnum):
    UZ = "uz"
    RU = "ru"
    EN = "en"

    @property
    def label(self) -> str:
        labels = {
            LanguageCode.UZ: "Uzbek",
            LanguageCode.RU: "Russian",
            LanguageCode.EN: "English",
        }
        return labels[self]

    @classmethod
    def supported(cls) -> tuple["LanguageCode", ...]:
        return (cls.UZ, cls.RU, cls.EN)

    @classmethod
    def selectable_sources(cls) -> tuple["LanguageCode", ...]:
        return cls.supported()
