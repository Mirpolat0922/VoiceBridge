import json
import time
from urllib import error, request

from voicebridge.domain.languages import LanguageCode
from voicebridge.schemas.text_pipeline import TextPipelineResult


class GroqTextPipelineError(RuntimeError):
    """Raised when the Groq text pipeline fails."""


class GroqTextPipeline:
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        endpoint: str,
        max_attempts: int,
        retry_base_delay_seconds: float,
        max_completion_tokens: int,
        timeout_seconds: float = 20.0,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name
        self._endpoint = endpoint
        self._max_attempts = max_attempts
        self._retry_base_delay_seconds = retry_base_delay_seconds
        self._max_completion_tokens = max_completion_tokens
        self._timeout_seconds = timeout_seconds

    def process(
        self,
        text: str,
        *,
        source_language: LanguageCode,
        target_language: LanguageCode,
    ) -> TextPipelineResult:
        if not self._api_key:
            raise GroqTextPipelineError("Groq API key is not configured.")

        if source_language is target_language:
            return TextPipelineResult(
                provider_name="groq_combined",
                source_language=source_language,
                target_language=target_language,
                source_text=text,
                translated_text=text,
            )

        payload = {
            "model": self._model_name,
            "temperature": 0.2,
            "max_tokens": self._max_completion_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Translate speech transcripts. Preserve meaning and tone. "
                        "Lightly fix obvious punctuation or casing only when needed "
                        "before translating. "
                        'Return valid JSON only: {"translated_text":"..."}'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Source language: {self._language_name(source_language)}\n"
                        f"Target language: {self._language_name(target_language)}\n"
                        f"Text:\n{text}"
                    ),
                },
            ],
        }

        response_payload = self._post_for_json(payload)
        translated_text = str(response_payload.get("translated_text", "")).strip()
        if not translated_text:
            raise GroqTextPipelineError("Groq text pipeline returned incomplete data.")

        return TextPipelineResult(
            provider_name="groq_combined",
            source_language=source_language,
            target_language=target_language,
            source_text=text,
            translated_text=translated_text,
        )

    def _post_for_json(self, payload: dict[str, object]) -> dict[str, str]:
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "VoiceBridge/0.1 (+https://api.groq.com/openai/v1)",
        }
        last_error: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                http_request = request.Request(
                    self._endpoint,
                    data=body,
                    headers=headers,
                    method="POST",
                )
                with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                    response_payload = json.loads(response.read().decode("utf-8"))
                content = str(response_payload["choices"][0]["message"]["content"]).strip()
                parsed_payload = json.loads(content)
                if not isinstance(parsed_payload, dict):
                    raise GroqTextPipelineError("Groq text pipeline returned invalid JSON.")
                return parsed_payload
            except error.HTTPError as http_error:
                last_error = http_error
                if self._is_rate_limit_status(http_error.code):
                    raise GroqTextPipelineError(
                        self._format_rate_limit_error(http_error)
                    ) from http_error
                if not self._is_retryable_status(http_error.code):
                    raise GroqTextPipelineError(
                        self._format_http_error(http_error, "Groq text pipeline failed.")
                    ) from http_error
            except error.URLError as url_error:
                last_error = url_error
            except json.JSONDecodeError as parse_error:
                raise GroqTextPipelineError(
                    "Groq text pipeline returned invalid JSON."
                ) from parse_error
            except (KeyError, IndexError, TypeError, ValueError) as parse_error:
                raise GroqTextPipelineError(
                    "Groq text pipeline response was invalid."
                ) from parse_error

            if attempt < self._max_attempts:
                time.sleep(self._retry_base_delay_seconds * (2 ** (attempt - 1)))

        if isinstance(last_error, error.HTTPError):
            raise GroqTextPipelineError(
                self._format_http_error(last_error, "Groq text pipeline failed.")
            ) from last_error
        raise GroqTextPipelineError("Groq text pipeline failed.") from last_error

    @staticmethod
    def _language_name(language: LanguageCode) -> str:
        mapping = {
            LanguageCode.UZ: "Uzbek",
            LanguageCode.RU: "Russian",
            LanguageCode.EN: "English",
        }
        return mapping.get(language, language.value)

    @staticmethod
    def _is_retryable_status(status_code: int) -> bool:
        return status_code in {408, 429, 500, 502, 503, 504}

    @staticmethod
    def _is_rate_limit_status(status_code: int) -> bool:
        return status_code == 429

    @staticmethod
    def _format_rate_limit_error(http_error: error.HTTPError) -> str:
        retry_after = http_error.headers.get("retry-after")
        if retry_after:
            return f"Groq rate limit reached. Try again in about {retry_after}s."
        return "Groq rate limit reached. Please try again later."

    @classmethod
    def _format_http_error(
        cls, http_error: error.HTTPError, fallback_message: str
    ) -> str:
        details = cls._extract_http_error_details(http_error)
        if details:
            return f"{fallback_message} {details}"
        return fallback_message

    @staticmethod
    def _extract_http_error_details(http_error: error.HTTPError) -> str:
        if http_error.fp is None:
            return f"(HTTP {http_error.code})."

        try:
            raw_body = http_error.read().decode("utf-8", errors="replace").strip()
        except Exception:
            return f"(HTTP {http_error.code})."

        if not raw_body:
            return f"(HTTP {http_error.code})."

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError:
            return f"(HTTP {http_error.code}) {raw_body[:300]}"

        error_payload = parsed.get("error")
        if isinstance(error_payload, dict):
            message = error_payload.get("message")
            code = error_payload.get("code")
            type_ = error_payload.get("type")
            parts = [f"HTTP {http_error.code}"]
            if code:
                parts.append(f"code={code}")
            if type_:
                parts.append(f"type={type_}")
            prefix = f"({' '.join(parts)})"
            if message:
                return f"{prefix} {message}"
            return prefix

        return f"(HTTP {http_error.code}) {raw_body[:300]}"
