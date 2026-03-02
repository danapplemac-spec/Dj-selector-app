# DJ Selector App (Engine-first MVP)

A modular desktop DJ mixing MVP with a thin Tkinter placeholder UI and a decoupled internal API.

## Features
- Two decks (A/B): load, play/pause, cue, seek, tempo, gain, key-lock flag.
- Mixer: crossfader, per-deck volume, 3-band EQ values, master gain.
- Library: folder scan, metadata extraction, SQLite persistence, search/sort.
- Analysis: BPM detection, beatgrid, downbeat estimate, key estimate (Camelot label), waveform generation.
- Helpers: sync, 8 hotcues (API-level support), looping (1/2/4/8/16 beats via command), master recording to WAV.
- Controls: keyboard mapping, optional basic MIDI mapping.
- Internal command/event API for future UI replacement.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Project structure
- `engine/`: playback decks, mixer, output stream, recording.
- `analysis/`: async-capable analysis helpers (BPM/key/beatgrid/waveform).
- `library/`: scanner + SQLite DB adapter.
- `controls/`: keyboard and MIDI mappings.
- `api/`: public command methods and event bus.
- `ui/`: minimal Tkinter placeholder.

## Internal API (commands)
- `loadTrack(deck, path)`
- `play(deck)`, `pause(deck)`, `togglePlay(deck)`
- `cue(deck)`, `seek(deck, seconds)`
- `setTempo(deck, value)`, `setGain(deck, value)`, `setVolume(deck, value)`
- `setEQ(deck, band, value)`, `setFilter(deck, value)`
- `setCrossfader(value)`, `sync(target, source)`
- `setHotcue(deck, index)`, `jumpHotcue(deck, index)`
- `setLoop(deck, length_beats)`, `clearLoop(deck)`
- `startRecording()`, `stopRecording(path)`
- `scanLibrary(folder)`, `searchLibrary(query, sortBy)`, `analyzeTrack(path)`

## Events
- `onTrackLoaded`, `onTransportState`, `onCue`
- `onTrackIndexed`, `onLibraryScanned`
- `onAnalysisComplete`, `onSync`
- `onHotcueSet`, `onHotcueJump`
- `onLoopSet`, `onLoopCleared`
- `onRecording`, `onAudioStatus`

See `docs/ARCHITECTURE.md` and `docs/NEXT_UI.md` for integration details.
