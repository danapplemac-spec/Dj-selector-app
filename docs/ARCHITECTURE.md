# Architecture

## Engine/UI separation
The application is built around `api.controller.DJApiController`.

- UI layer calls **commands** on the controller.
- Controller mutates engine/library state and emits **events** through `EventBus`.
- UI subscribes to events and re-renders.
- No UI code reaches into audio engine internals.

This allows replacing `ui/` with another frontend (Qt, web, touch UI, radial UI) while preserving engine behavior.

## Modules
- `engine.deck.DeckState`: track buffer, transport state, hotcues, loop state, chunk rendering.
- `engine.mixer.MixerEngine`: real-time callback, crossfader curves, master mix, recording.
- `library.database.LibraryDB`: SQLite schema and persistence (tracks/hotcues/loops).
- `library.scanner`: folder crawling and metadata extraction.
- `analysis.analyzer`: BPM/key/downbeat/waveform analysis.
- `api.events.EventBus`: event subscription and fan-out.
- `api.controller.DJApiController`: stable internal API boundary.

## Event-driven flow
1. UI dispatches `loadTrack(deck, path)`.
2. Controller loads deck and emits `onTrackLoaded`.
3. UI starts analysis (`analyzeTrack`) and receives `onAnalysisComplete`.
4. During playback, UI sends transport/mixer commands.
5. Recorder is controlled via `startRecording` / `stopRecording`.

## Notes
- Key-lock is currently modeled as a flag; production-grade time-stretch would require an external DSP backend.
- PFL/headphone routing is left as a future enhancement due to hardware/output complexity.
