from voicebridge.domain.languages import LanguageCode


def test_selectable_sources_include_auto_and_supported_languages() -> None:
    assert LanguageCode.selectable_sources() == (
        LanguageCode.AUTO,
        LanguageCode.UZ,
        LanguageCode.RU,
        LanguageCode.EN,
    )


def test_supported_languages_include_translation_targets() -> None:
    assert LanguageCode.supported() == (
        LanguageCode.UZ,
        LanguageCode.RU,
        LanguageCode.EN,
    )
