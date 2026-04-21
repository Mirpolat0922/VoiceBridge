# VoiceBridge Project History

## Purpose Of This Document

This file preserves the practical history behind the current project, including experiments,
rejected approaches, and the reasoning that led to the final architecture. It is intended as a
learning document for understanding not just what the project does now, but why it ended up in
its current form.

## Product Goal

VoiceBridge started as a multilingual Telegram voice bot with three main goals:

1. Accept voice notes from Telegram.
2. Translate between Uzbek, Russian, and English.
3. Optionally return translated speech.

From the beginning, English and Russian were treated as the stable path, while Uzbek was handled
more honestly as a beta-quality feature.

## Major Implementation Phases

### 1. Core Bot And Settings

The first layer of the project established:

- the Telegram bot entrypoint
- typed environment settings
- SQLite-backed per-user preferences
- source language, target language, and reply mode controls

This created a stable shell around the future speech pipeline.

### 2. Audio Pipeline

Telegram voice notes arrive as compressed OGG/Opus files. The project introduced a dedicated
audio service to:

- download the incoming file
- convert it to mono 16 kHz WAV with `ffmpeg`
- hand a normalized format to the ASR layer

This separation mattered because speech models behave more predictably on consistent input audio.

### 3. ASR Routing

The initial design already assumed that one ASR model might not be best for every language.
That led to a routed ASR service:

- `faster-whisper` for `auto`, Russian, and English
- NVIDIA NeMo Uzbek ASR for explicit Uzbek mode

This decision came from practical testing: Whisper was reasonable for Russian and English, but
less trustworthy on Uzbek.

## Text-Processing Experiments

### Early Idea: Separate Cleanup And Translation

An earlier version of the project treated transcript cleanup and translation as separate steps.
That approach was useful for learning because it made the pipeline easy to explain:

- ASR produced raw text
- a cleanup model repaired punctuation and casing
- a translation model produced the target-language output

This was conceptually neat, but it increased request count and operational complexity.

### Gemini Phase

Gemini was adopted because the text quality was strong in practical testing. The project explored:

- transcript cleanup with Gemini
- translation with Gemini
- later, a combined cleanup-and-translation Gemini request

Why Gemini was attractive:

- good output quality
- flexible prompt-based text transformation
- easy experimentation during development

Why Gemini became a problem:

- free-tier quota pressure was hit very quickly during repeated testing
- retry logic and model fallbacks multiplied API calls
- a single message could trigger more than one LLM request

The key lesson from this phase was that quality alone is not enough. Cost, quota behavior, and
failure-mode simplicity matter in a real bot.

### Official Translation API Experiments

The project also explored official translation APIs such as Azure Translator and Google Cloud
Translation.

Why they were considered:

- simpler “translation-only” semantics
- less prompt engineering
- potentially more predictable than LLM prompting

Why they were not kept:

- account and billing setup friction
- less attractive for fast portfolio iteration
- they did not beat the practical simplicity of the final path enough to justify staying

## TTS Experiments

Voice reply support went through multiple phases.

### `gTTS`

Pros:

- easy to install
- easy to integrate
- enough to prove the feature

Cons:

- robotic quality

### Other TTS Paths

The project also experimented with stronger TTS paths such as `edge-tts` and cloud speech
providers. These were useful for exploration, but they made the repo heavier and were eventually
removed when the project was simplified around the working portfolio path.

## UX Iteration History

The Telegram UX also evolved over time.

Early versions leaned more on plain commands. Later versions added:

- inline keyboards
- a reusable `/start` control center
- in-message settings access
- stable result messages that are not overwritten by later control interactions

The main lesson here was that speech pipelines often take long enough that visible progress
updates matter. The project now edits a processing message through the major pipeline stages so
Telegram does not feel frozen.

## Why The Final Architecture Is Simpler

The final version intentionally removed a lot of historical fallback logic.

Current production path:

1. Telegram voice note
2. audio normalization
3. ASR
4. one Groq post-processing + translation request
5. optional `gTTS`

This simplified version was chosen because it:

- matches the actual portfolio goal better
- reduces confusion while reading the codebase
- avoids wasteful fallback chains
- keeps the repo easier to maintain and explain

## Techniques Used In The Final Project

- service-layer separation
- provider-based ASR routing
- environment-driven configuration
- SQLite repository pattern for user settings
- temporary-file cleanup after request completion
- prompt-based post-processing and translation with Groq
- structured Telegram UX with inline keyboards and command support

## What To Learn From This Project

If you want to study the project deeply, focus on these ideas:

- Why audio normalization happens before ASR
- Why ASR routing is language-aware
- Why Uzbek is explicitly labeled beta
- Why a simple runtime path is often better than many backup providers
- Why temporary-file cleanup matters in media-processing apps
- Why “works locally” and “sustainable under quota limits” are different engineering problems

## Current Recommendation

For understanding the current codebase, read in this order:

1. [README.md](../README.md)
2. [architecture.md](./architecture.md)
3. [deep-dive.md](./deep-dive.md)
4. [interview-guide.md](./interview-guide.md)
5. the runtime path in `src/voicebridge/bot/app.py` and `src/voicebridge/bot/handlers/voice.py`
