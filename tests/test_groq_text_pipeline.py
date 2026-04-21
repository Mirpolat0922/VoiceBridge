import io
import json
from urllib import error

import pytest

from voicebridge.domain.languages import LanguageCode
from voicebridge.services.pipeline.text_pipeline import GroqTextPipeline, GroqTextPipelineError


class FakeHttpResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_groq_text_pipeline_returns_translation(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = GroqTextPipeline(
        api_key="test-key",
        model_name="llama-3.3-70b-versatile",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        max_attempts=1,
        retry_base_delay_seconds=0.01,
        max_completion_tokens=300,
    )

    def fake_urlopen(http_request, timeout):
        return FakeHttpResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"translated_text": "Hello world"}),
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "voicebridge.services.pipeline.text_pipeline.request.urlopen",
        fake_urlopen,
    )

    result = pipeline.process(
        "Привет мир",
        source_language=LanguageCode.RU,
        target_language=LanguageCode.EN,
    )

    assert result.provider_name == "groq_combined"
    assert result.translated_text == "Hello world"


def test_groq_text_pipeline_reuses_source_when_languages_match() -> None:
    pipeline = GroqTextPipeline(
        api_key="test-key",
        model_name="llama-3.3-70b-versatile",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        max_attempts=1,
        retry_base_delay_seconds=0.01,
        max_completion_tokens=300,
    )

    result = pipeline.process(
        "Hello world",
        source_language=LanguageCode.EN,
        target_language=LanguageCode.EN,
    )

    assert result.translated_text == "Hello world"


def test_groq_text_pipeline_surfaces_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = GroqTextPipeline(
        api_key="test-key",
        model_name="llama-3.3-70b-versatile",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        max_attempts=1,
        retry_base_delay_seconds=0.01,
        max_completion_tokens=300,
    )

    def fake_urlopen(http_request, timeout):
        raise error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=429,
            msg="rate limit",
            hdrs={"retry-after": "45"},
            fp=None,
        )

    monkeypatch.setattr(
        "voicebridge.services.pipeline.text_pipeline.request.urlopen",
        fake_urlopen,
    )

    with pytest.raises(GroqTextPipelineError, match="Groq rate limit reached"):
        pipeline.process(
            "Привет",
            source_language=LanguageCode.RU,
            target_language=LanguageCode.UZ,
        )


def test_groq_text_pipeline_includes_http_error_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = GroqTextPipeline(
        api_key="test-key",
        model_name="llama-3.3-70b-versatile",
        endpoint="https://api.groq.com/openai/v1/chat/completions",
        max_attempts=1,
        retry_base_delay_seconds=0.01,
        max_completion_tokens=300,
    )

    def fake_urlopen(http_request, timeout):
        raise error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=403,
            msg="forbidden",
            hdrs={},
            fp=io.BytesIO(
                json.dumps(
                    {
                        "error": {
                            "message": "Project does not have access to the requested model.",
                            "type": "invalid_request_error",
                            "code": "project_model_denied",
                        }
                    }
                ).encode("utf-8")
            ),
        )

    monkeypatch.setattr(
        "voicebridge.services.pipeline.text_pipeline.request.urlopen",
        fake_urlopen,
    )

    with pytest.raises(GroqTextPipelineError, match="project_model_denied"):
        pipeline.process(
            "Привет",
            source_language=LanguageCode.RU,
            target_language=LanguageCode.UZ,
        )
