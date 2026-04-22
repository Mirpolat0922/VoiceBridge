# VoiceBridge

VoiceBridge is a Telegram bot that accepts a voice message in Uzbek, Russian, or English and
replies with:

- the transcript
- the translated text
- an optional translated voice reply

## Overview

The project uses one clear production path:

`Telegram voice -> audio normalization -> ASR -> Groq post-processing + translation -> optional gTTS`

## Current Stack

- Telegram bot framework: `aiogram`
- Audio normalization: `ffmpeg`
- ASR:
  - `faster-whisper` for Russian and English
  - NVIDIA NeMo Uzbek ASR for explicit Uzbek mode
- Text post-processing and translation: Groq `llama-3.3-70b-versatile`
- Voice reply: `gTTS`
- User settings storage: SQLite

## Features

- Telegram voice-note input
- Language-aware ASR routing
- Uzbek, Russian, and English support
- Optional translated voice replies
- Per-user settings for source language, target language, and reply mode
- Inline Telegram control center and settings keyboard

## Architecture

- `audio` service downloads and normalizes Telegram media
- `asr` service routes by language
- `pipeline` service sends the transcript to Groq for post-processing and translation
- `tts` service optionally generates a translated voice reply
- `storage` persists per-user settings in SQLite

## Project Structure

```text
src/voicebridge/
  bot/            Telegram transport and handlers
  config/         Environment-backed settings
  domain/         Shared enums and language concepts
  schemas/        Request and response models
  services/       Audio, ASR, text pipeline, TTS, and user settings
  storage/        SQLite persistence
  utils/          Logging and runtime helpers
```

## Local Development

Use Python `3.11`, especially on macOS for the optional Uzbek ASR path.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m voicebridge.main
```

For the optional Uzbek ASR provider:

```bash
brew install cmake
pip install -e ".[dev,uzbek_asr]"
```

## Required `.env` Settings

```env
VOICEBRIDGE_BOT_TOKEN=your_telegram_bot_token
VOICEBRIDGE_GROQ_API_KEY=your_groq_key
VOICEBRIDGE_GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

Other Groq settings have sensible defaults in `.env.example`.

The bot supports these user commands:

```text
/start
/settings
/source uz|ru|en
/target uz|ru|en
/reply text_only|text_and_voice
```

## Behavior Notes

- Uzbek is explicitly treated as beta.
- Users should choose the exact source language before sending a voice note.
- Temporary input audio, normalized WAV files, and generated TTS files are deleted after each
  request.
- User settings are stored in SQLite; transcript history is not stored separately because
  Telegram already acts as visible history.

## Limitations

- Uzbek quality is less predictable than Russian and English.
- `gTTS` is practical but not premium-quality speech synthesis.
- Long voice notes can still feel slow because ASR and translation happen inline.

## Documentation

- [Architecture](./docs/architecture.md)
- [Deep Dive](./docs/deep-dive.md)
- [Interview Guide](./docs/interview-guide.md)
- [Project History](./docs/project-history.md)
- [Roadmap](./docs/roadmap.md)
