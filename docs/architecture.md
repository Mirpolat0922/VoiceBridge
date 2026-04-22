# VoiceBridge Architecture

## Purpose

VoiceBridge is a compact multilingual speech pipeline for Telegram. The bot layer stays thin,
while the core work happens in focused services for audio normalization, ASR, text processing,
TTS, and user settings.

## High-Level Flow

1. Telegram sends a voice message update.
2. The bot downloads the voice note and normalizes it to mono 16 kHz WAV.
3. The ASR service transcribes the audio using a language-aware provider.
4. The Groq text pipeline lightly cleans obvious ASR formatting issues while translating.
5. If enabled, `gTTS` generates a translated voice reply.
6. The bot edits the progress message into the final result and optionally sends voice output.
7. Temporary files are deleted after the request finishes.

## Main Modules

### `bot/`

Telegram-specific startup, handlers, and inline UI.

### `config/`

Typed environment-backed settings.

### `domain/`

Shared enums such as supported languages and reply modes.

### `services/audio/`

Downloads Telegram media and normalizes it for ASR.

### `services/asr/`

Routes by language:

- `faster-whisper` for Russian and English
- NVIDIA NeMo Uzbek ASR for explicit Uzbek mode

### `services/pipeline/`

Contains the Groq text pipeline that post-processes ASR output and translates it in one request.

### `services/tts/`

Provides optional translated voice replies with `gTTS`.

### `services/user_settings.py` and `storage/`

Store per-user source language, target language, and reply mode in SQLite.

## Design Choices

- Keep the Telegram layer small.
- Be honest that Uzbek is beta.
- Use one clear production text path instead of several parked fallbacks.
- Store only user settings in SQLite and rely on Telegram as the visible conversation history.
- Clean up temporary audio artifacts aggressively.

## Current Product Path

The project intentionally uses a single post-ASR text path now:

`ASR transcript -> Groq llama-3.3-70b-versatile -> translated text`

This keeps the project easier to reason about, cheaper to run on a free-tier portfolio setup,
and less fragile than a many-provider fallback graph.
