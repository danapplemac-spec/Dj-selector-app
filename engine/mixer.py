from __future__ import annotations

import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from api.events import EventBus
from engine.deck import DeckState


class MixerEngine:
    def __init__(self, events: EventBus, sample_rate: int = 44100, block_size: int = 1024) -> None:
        self.events = events
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.decks = {"A": DeckState("A"), "B": DeckState("B")}
        self.crossfader = 0.5
        self.master_gain = 1.0
        self.stream: sd.OutputStream | None = None
        self.recording = False
        self.record_buffer: list[np.ndarray] = []
        self._lock = threading.Lock()

    def start(self) -> None:
        if self.stream:
            return
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=2,
            blocksize=self.block_size,
            dtype="float32",
            callback=self._callback,
        )
        self.stream.start()

    def stop(self) -> None:
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def _callback(self, outdata: np.ndarray, frames: int, _time, status) -> None:
        if status:
            self.events.emit("onAudioStatus", status=str(status))
        with self._lock:
            left_weight = np.cos(self.crossfader * np.pi / 2)
            right_weight = np.sin(self.crossfader * np.pi / 2)
            a = self.decks["A"].render_chunk(self.sample_rate, frames) * left_weight
            b = self.decks["B"].render_chunk(self.sample_rate, frames) * right_weight
            mixed = (a + b) * self.master_gain
            np.clip(mixed, -1.0, 1.0, out=mixed)
            outdata[:] = mixed
            if self.recording:
                self.record_buffer.append(mixed.copy())

    def set_crossfader(self, value: float) -> None:
        self.crossfader = float(np.clip(value, 0.0, 1.0))

    def sync_decks(self, target: str = "A", source: str = "B") -> None:
        t = self.decks[target]
        s = self.decks[source]
        if t.bpm > 0 and s.bpm > 0:
            t.tempo = s.bpm / t.bpm
            t.playhead = s.playhead
            self.events.emit("onSync", target=target, source=source, tempo=t.tempo)

    def start_recording(self) -> None:
        with self._lock:
            self.recording = True
            self.record_buffer.clear()
        self.events.emit("onRecording", active=True)

    def stop_recording(self, output_path: Path) -> None:
        with self._lock:
            self.recording = False
            if self.record_buffer:
                data = np.concatenate(self.record_buffer, axis=0)
                sf.write(output_path, data, self.sample_rate)
                self.record_buffer.clear()
        self.events.emit("onRecording", active=False, path=str(output_path))
