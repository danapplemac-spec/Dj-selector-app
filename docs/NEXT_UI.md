# Replacing the Placeholder UI

## Goal
Build your own UI without touching engine internals.

## Contract to keep
Use only `DJApiController` commands and events.

### Command pattern
```python
api = DJApiController(Path("library.db"))
api.start_audio()
api.loadTrack("A", "/music/track1.wav")
api.play("A")
api.setCrossfader(0.25)
```

### Event subscription
```python
def on_any(evt):
    print(evt.name, evt.payload)

api.on("*", on_any)
```

## UI migration checklist
1. Keep one controller instance alive for app lifetime.
2. Subscribe to transport/library/analysis events.
3. Dispatch user actions as commands.
4. Do not read/modify `engine.*` objects directly.
5. Add your own view models around event payloads.

## Suggested extensions
- Replace Tkinter with a custom touch-first UI toolkit.
- Add async job queue for analysis to avoid UI stalls.
- Add dedicated waveform widget with beat markers + zoom overlays.
- Add MIDI learn mode and persistent mapping table.
