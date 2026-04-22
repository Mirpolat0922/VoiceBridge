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

## Setup And Run

Use Python `3.11`. The commands below install the full project, including Uzbek ASR support.

### 1. Clone The Repository

```bash
git clone https://github.com/Mirpolat0922/VoiceBridge.git
cd VoiceBridge
```

### 2. Install System Dependencies

VoiceBridge needs `ffmpeg` for audio conversion and `cmake` for the full Uzbek ASR setup.

**macOS**

```bash
brew install ffmpeg cmake
```

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install -y ffmpeg cmake
```

**Windows**

- Install Python `3.11`
- Install `ffmpeg` and make sure it is available in `PATH`
- Install `cmake` and make sure it is available in `PATH`

### 3. Create A Virtual Environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install Python Dependencies

```bash
pip install -e ".[dev,uzbek_asr]"
```

### 5. Create The Environment File

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
copy .env.example .env
```

Then open `.env` and set at least:

```env
VOICEBRIDGE_BOT_TOKEN=your_telegram_bot_token
VOICEBRIDGE_GROQ_API_KEY=your_groq_key
VOICEBRIDGE_GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

Other Groq settings already have sensible defaults in `.env.example`.

### 6. Run The Bot

```bash
python -m voicebridge.main
```

### First Run Notes

- `faster-whisper` downloads its model the first time it is used.
- The NeMo Uzbek model is downloaded the first time Uzbek ASR is used.
- `gTTS` and Groq require internet access.
- First-run setup can be noticeably slower because model files are being downloaded.

## Required `.env` Settings

```env
VOICEBRIDGE_BOT_TOKEN=your_telegram_bot_token
VOICEBRIDGE_GROQ_API_KEY=your_groq_key
VOICEBRIDGE_GROQ_MODEL_NAME=llama-3.3-70b-versatile
```

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
