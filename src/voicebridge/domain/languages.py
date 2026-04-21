from enum import StrEnum


class LanguageCode(StrEnum):
    AUTO = "auto"
    UZ = "uz"
    RU = "ru"
    EN = "en"

    @classmethod
    def supported(cls) -> tuple["LanguageCode", ...]:
        return (cls.UZ, cls.RU, cls.EN)

    @classmethod
    def selectable_sources(cls) -> tuple["LanguageCode", ...]:
        return (cls.AUTO, cls.UZ, cls.RU, cls.EN)
