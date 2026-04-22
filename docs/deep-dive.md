# VoiceBridge Deep Dive

## Current End-To-End Pipeline

1. User sends a Telegram voice note.
2. Telegram bot downloads the OGG/Opus file.
3. Audio service converts it into mono 16 kHz WAV.
4. ASR service routes by language:
   - Uzbek -> NVIDIA NeMo FastConformer
   - Russian / English -> faster-whisper
5. Groq `llama-3.3-70b-versatile` post-processes the transcript and translates it in one call.
6. If reply mode is `text_and_voice`, `gTTS` generates a translated voice reply.
7. Bot edits the progress message into the final text result and optionally sends the voice reply.
8. Temporary audio and TTS files are cleaned up after the request.

## Why The Text Path Is Simple

The project used to carry multiple fallback providers and text stages. It is intentionally
simpler now:

- one ASR result goes into one Groq text request
- that request lightly fixes obvious ASR formatting issues and translates
- there is no provider cascade after that

This makes the code easier to reason about and avoids quota burn caused by fallback chains.

## Models In Use

### ASR

- `faster-whisper`
  - used for English and Russian
- `nvidia/stt_uz_fastconformer_hybrid_large_pc`
  - used for explicit Uzbek mode
  - still treated as beta

### Text Pipeline

- Groq `llama-3.3-70b-versatile`
  - used for transcript post-processing and translation
  - returns the final translated text in one request

### TTS

- `gTTS`
  - used for optional translated voice replies
  - pragmatic and easy to run locally

## Important Product Decisions

### Telegram Is The Visible History

The bot stores user settings in SQLite, but it does not maintain a separate transcript history.
Telegram itself acts as the visible conversation record.

### Uzbek Is Explicitly Beta

This is a deliberate product choice. Uzbek support works, but quality is still less predictable
than Russian and English.

### Temporary Files Are Disposable

The project only keeps temporary audio artifacts needed during processing:

- downloaded Telegram audio
- normalized WAV audio
- generated TTS output

These files are deleted after each request.

## Why This Version Is Better For The Portfolio

- The runtime path is easy to explain.
- The codebase is smaller and cleaner.
- The behavior matches the documentation.
- The project still shows realistic AI-system boundaries without carrying dead provider code.
