from __future__ import annotations

import json
from pathlib import Path

from analysis.analyzer import analyze_track
from api.events import EventBus
from engine.mixer import MixerEngine
from library.database import LibraryDB
from library.scanner import extract_metadata, scan_audio_files


class DJApiController:
    def __init__(self, db_path: Path) -> None:
        self.events = EventBus()
        self.db = LibraryDB(db_path)
        self.engine = MixerEngine(self.events)

    # Commands
    def start_audio(self) -> None:
        self.engine.start()

    def stop_audio(self) -> None:
        self.engine.stop()

    def scanLibrary(self, folder: str) -> int:
        count = 0
        for path in scan_audio_files(Path(folder)):
            row = extract_metadata(path)
            track_id = self.db.upsert_track({
                **row,
                "bpm": None,
                "musical_key": None,
                "beatgrid_json": None,
                "waveform_json": None,
            })
            self.events.emit("onTrackIndexed", trackId=track_id, path=str(path))
            count += 1
        self.events.emit("onLibraryScanned", count=count)
        return count

    def analyzeTrack(self, path: str) -> None:
        base = self.db.get_track_by_path(path)
        if not base:
            return
        details = analyze_track(Path(path))
        self.db.upsert_track({**base, **details})
        self.events.emit("onAnalysisComplete", path=path, bpm=details["bpm"], musicalKey=details["musical_key"])

    def loadTrack(self, deck: str, path: str) -> None:
        state = self.engine.decks[deck]
        state.load(Path(path))
        entry = self.db.get_track_by_path(path)
        if entry:
            state.bpm = entry.get("bpm") or state.bpm
            state.hotcues = self.db.get_hotcues(entry["id"])
        self.events.emit("onTrackLoaded", deck=deck, path=path)

    def play(self, deck: str) -> None:
        self.engine.decks[deck].is_playing = True
        self.events.emit("onTransportState", deck=deck, state="playing")

    def pause(self, deck: str) -> None:
        self.engine.decks[deck].is_playing = False
        self.events.emit("onTransportState", deck=deck, state="paused")

    def togglePlay(self, deck: str) -> None:
        deck_state = self.engine.decks[deck]
        deck_state.is_playing = not deck_state.is_playing
        self.events.emit("onTransportState", deck=deck, state="playing" if deck_state.is_playing else "paused")

    def cue(self, deck: str) -> None:
        self.engine.decks[deck].cue()
        self.events.emit("onCue", deck=deck)

    def seek(self, deck: str, seconds: float) -> None:
        self.engine.decks[deck].seek(seconds)

    def setTempo(self, deck: str, value: float) -> None:
        self.engine.decks[deck].tempo = value

    def setGain(self, deck: str, value: float) -> None:
        self.engine.decks[deck].gain = value

    def setVolume(self, deck: str, value: float) -> None:
        self.engine.decks[deck].volume = value

    def setEQ(self, deck: str, band: str, value: float) -> None:
        state = self.engine.decks[deck]
        setattr(state, f"eq_{band}", value)

    def setFilter(self, deck: str, value: float) -> None:
        self.engine.decks[deck].filter_amt = value

    def setCrossfader(self, value: float) -> None:
        self.engine.set_crossfader(value)

    def sync(self, target: str, source: str) -> None:
        self.engine.sync_decks(target=target, source=source)

    def setHotcue(self, deck: str, index: int) -> None:
        state = self.engine.decks[deck]
        if not state.loaded_path:
            return
        entry = self.db.get_track_by_path(state.loaded_path)
        if not entry:
            return
        seconds = state.playhead / state.sample_rate
        self.db.set_hotcue(entry["id"], index, seconds)
        state.hotcues[index] = seconds
        self.events.emit("onHotcueSet", deck=deck, index=index, seconds=seconds)

    def jumpHotcue(self, deck: str, index: int) -> None:
        state = self.engine.decks[deck]
        if index in state.hotcues:
            state.seek(state.hotcues[index])
            self.events.emit("onHotcueJump", deck=deck, index=index)

    def setLoop(self, deck: str, length_beats: int) -> None:
        state = self.engine.decks[deck]
        if not state.loaded_path:
            return
        start = state.playhead / state.sample_rate
        state.set_loop(start, length_beats)
        entry = self.db.get_track_by_path(state.loaded_path)
        if entry:
            self.db.set_loop(entry["id"], 0, start, length_beats)
        self.events.emit("onLoopSet", deck=deck, start=start, lengthBeats=length_beats)

    def clearLoop(self, deck: str) -> None:
        self.engine.decks[deck].clear_loop()
        self.events.emit("onLoopCleared", deck=deck)

    def startRecording(self) -> None:
        self.engine.start_recording()

    def stopRecording(self, path: str) -> None:
        self.engine.stop_recording(Path(path))

    def searchLibrary(self, query: str, sortBy: str = "title") -> list[dict]:
        return self.db.list_tracks(query, sortBy)

    def getWaveform(self, path: str) -> list[float]:
        row = self.db.get_track_by_path(path)
        if not row or not row.get("waveform_json"):
            return []
        return json.loads(row["waveform_json"])

    # event helper
    def on(self, event_name: str, callback) -> None:
        self.events.subscribe(event_name, callback)
