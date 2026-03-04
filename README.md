# DJ Selector App (Engine-first MVP)

A modular desktop DJ mixing MVP with a thin Tkinter placeholder UI and a decoupled internal API.

## What you need to run it
- Python 3.10+
- Working audio device/output
- `pip` able to install Python packages

## 1) Create environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Windows one-command bootstrap (PowerShell)
From the repo root:

```powershell
./scripts/dev-setup-windows.ps1
```

If your system blocks local scripts, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev-setup-windows.ps1
```

Or use the batch wrapper:

```bat
scripts\dev-setup-windows.bat
```

What this does:
- checks Python launcher (`py`)
- optionally tries to install `libsndfile` via `winget`
- creates `.venv`
- upgrades pip tooling
- installs `requirements.txt`

Optional flags:

```powershell
./scripts/dev-setup-windows.ps1 -SkipWinget
./scripts/dev-setup-windows.ps1 -SkipPipInstall
```

## 2) Start the app
```bash
python main.py
```

## 3) Use the MVP UI
1. Click **Scan Folder** and pick a local music folder.
2. Double-click a track (or use **Load Selected**) to load on deck A/B.
3. Press **Play/Pause** on each deck.
4. Move the crossfader in **Mixer**.
5. Press **Start Rec** / **Stop Rec** to write `recording.wav`.

## Keyboard shortcuts
- `Space`: toggle deck A
- `Enter`: toggle deck B
- `Z`: cue deck A
- `M`: cue deck B
- `S`: sync A to B
- `K`: sync B to A

## If it does not start (most common fixes)

### Missing system audio libraries (Linux)
Install PortAudio and libsndfile development/runtime packages:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y portaudio19-dev libsndfile1
```

### `pip install` fails for numpy/librosa
- Check internet/proxy settings.
- Ensure you are inside the virtualenv (`which python` should point to `.venv`).
- Retry with updated pip (`python -m pip install --upgrade pip`).

### App runs but analysis says unavailable
Analysis is optional at startup. The app now emits an analysis error event and continues running if `librosa` is missing. Install full requirements to enable BPM/key/waveform analysis.

## Windows packaging (EXE + installer)
You can now build a portable EXE and installer for Windows:

```powershell
./scripts/build-windows-package.ps1 -Version 0.1.0
```

Requirements:
- run `./scripts/dev-setup-windows.ps1` first
- install Inno Setup 6 (`ISCC.exe`)

CI release workflow:
- `.github/workflows/windows-release.yml`
- triggers on tags `v*` and `workflow_dispatch`
- uploads portable app + installer artifacts

See `docs/RELEASE_WINDOWS.md` for full release steps.

## CI
GitHub Actions workflow includes:
- Linux test job for Python modules (`pytest`).
- Windows job that runs `scripts/dev-setup-windows.ps1` and smoke-checks `python main.py` startup in CI mode.

## Features
- Two decks (A/B): load, play/pause, cue, seek, tempo, gain, key-lock flag.
- Mixer: crossfader, per-deck volume, 3-band EQ values, master gain.
- Library: folder scan, metadata extraction, SQLite persistence, search/sort.
- Analysis: BPM detection, beatgrid, downbeat estimate, key estimate (Camelot label), waveform generation.
- Helpers: sync, 8 hotcues (API-level support), looping (1/2/4/8/16 beats via command), master recording to WAV.
- Controls: keyboard mapping, optional basic MIDI mapping.
- Internal command/event API for future UI replacement.

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
- `onAnalysisComplete`, `onAnalysisError`, `onSync`
- `onHotcueSet`, `onHotcueJump`
- `onLoopSet`, `onLoopCleared`
- `onRecording`, `onAudioStatus`

See `docs/ARCHITECTURE.md` and `docs/NEXT_UI.md` for integration details.
