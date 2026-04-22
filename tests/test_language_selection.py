from voicebridge.domain.languages import LanguageCode


def test_selectable_sources_match_supported_languages() -> None:
    assert LanguageCode.selectable_sources() == LanguageCode.supported()


def test_supported_languages_include_translation_targets() -> None:
    assert LanguageCode.supported() == (
        LanguageCode.UZ,
        LanguageCode.RU,
        LanguageCode.EN,
    )
