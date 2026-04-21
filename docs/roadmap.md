# VoiceBridge Roadmap

## Completed

- Project scaffolding and typed configuration
- SQLite-backed user settings
- Telegram audio download and normalization
- Language-aware ASR routing
- Dedicated Uzbek ASR path
- Inline Telegram control center
- Optional translated voice replies with `gTTS`
- Groq-based transcript post-processing and translation
- Temporary-file cleanup and service-layer tests
- Codebase cleanup to remove unused provider paths

## Current State

The current product path is intentionally simple:

1. Telegram voice message
2. audio normalization
3. ASR
4. Groq post-processing + translation
5. optional `gTTS`

## Possible Later Improvements

- better TTS quality if a practical provider is found
- background-job handling for longer requests
- better operational logging and usage metrics
- more real-world evaluation data for Uzbek
