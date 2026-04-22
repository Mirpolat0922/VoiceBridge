# VoiceBridge Interview Guide

## One-Sentence Pitch

VoiceBridge is a Telegram bot that receives a voice message in Uzbek, Russian, or English, converts it to text, translates it, and returns translated text, with an optional translated voice reply.

## Why This Project Is Interesting

This project is not just a chatbot. It is a multilingual speech pipeline with several AI components that must work together:

- speech-to-text
- transcript post-processing
- translation
- optional text-to-speech
- language-aware routing
- Telegram bot UX

## Core Product Decision

The most important product decision is honesty about quality:

- English and Russian are primary supported languages.
- Uzbek is available in beta mode because open-source quality is less consistent.

That makes the product more trustworthy and reflects real AI engineering tradeoffs.

## Architecture Story

When explaining the project, emphasize that it is split into layers:

1. Telegram bot layer
2. audio preprocessing layer
3. ASR layer
4. Groq text pipeline
5. optional TTS layer
6. persistence layer

This makes the project easier to extend and easier to test.

## Audio Preprocessing Story

Telegram voice notes usually arrive as compressed Opus audio inside OGG containers. Most ASR models perform more predictably when input is normalized to a single format, so the project downloads the original file and converts it into a standard mono WAV file before transcription.

## Persistence Story

The project uses SQLite first because it is enough for a portfolio bot and keeps local setup simple. User preferences are stored through a repository and service layer so that the Telegram handlers do not depend on raw SQL.

## ASR Design Story

The project does not tie Telegram handlers directly to one speech model. Instead, it uses an ASR service with provider routing. That makes it possible to use one provider for English and Russian and a different provider for Uzbek later, without rewriting the rest of the bot.

In the current implementation, the user chooses the source language explicitly. This matters because Uzbek performs poorly under generic auto-detection in Whisper, so the product routes Uzbek requests to a dedicated provider instead of guessing.

## Text Pipeline Story

The project now uses a single Groq request after ASR. That request does two things at once:

- lightly fixes obvious ASR formatting issues
- translates into the user’s target language

This is a cleaner production story than carrying many backup providers in a portfolio project.
It keeps the runtime easy to understand and avoids wasting free-tier quota on fallback chains.

## Storage Story

The project intentionally keeps persistence minimal:

- user settings are stored in SQLite
- model caches are stored locally because the ML runtimes need them
- temporary audio files are deleted after the request completes, including failure paths
- transcripts and translations are not stored in a custom history database

This is a practical product decision because Telegram already acts as the visible chat history, and the local app should not silently accumulate large audio archives.

## TTS Story

The project uses `gTTS` as a simple optional voice mode because it is practical and easy to run,
even though the voice quality is still robotic.

## Why Avoid Hardcoding

The project is intentionally designed so language rules, providers, and defaults are configurable. That matters because speech models may change over time, and different languages often require different providers.

## Good Interview Talking Points

- Why Whisper was kept for Russian and English
- Why Uzbek needs a specialized ASR path
- Why the text path was simplified to one Groq call
- Why Uzbek is marked beta instead of pretending quality is solved
- Why the Telegram layer should stay thin
- Why temporary audio cleanup matters in a voice app

## Questions You May Get

### Why not use one model for everything?

Because multilingual quality is uneven. A better engineering choice is routing by language when one model does not perform well enough for all cases.

### Why label Uzbek as beta?

Because it is better product design to be transparent about quality than to promise equal accuracy when the open-source ecosystem is weaker for that language.

### How would you scale this later?

By moving heavy model execution into dedicated workers, adding job queues, object storage, and better metrics, while keeping the same service boundaries.
