from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass
class DeckState:
    name: str
    loaded_path: str | None = None
    samples: np.ndarray | None = None
    sample_rate: int = 44100
    playhead: float = 0.0
    is_playing: bool = False
    tempo: float = 1.0
    key_lock: bool = False
    gain: float = 1.0
    volume: float = 1.0
    eq_low: float = 1.0
    eq_mid: float = 1.0
    eq_high: float = 1.0
    filter_amt: float = 0.0
    hotcues: dict[int, float] = field(default_factory=dict)
    loop_active: bool = False
    loop_start: float = 0.0
    loop_end: float = 0.0
    bpm: float = 120.0

    def load(self, path: Path) -> None:
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        self.samples = data
        self.sample_rate = sr
        self.playhead = 0.0
        self.is_playing = False
        self.loaded_path = str(path)

    def seek(self, seconds: float) -> None:
        if self.samples is None:
            return
        self.playhead = max(0.0, min(seconds * self.sample_rate, len(self.samples) - 1))

    def cue(self) -> None:
        self.seek(0.0)
        self.is_playing = False

    def set_loop(self, start: float, length_beats: int) -> None:
        beat_seconds = 60.0 / max(self.bpm, 1.0)
        self.loop_start = start
        self.loop_end = start + (beat_seconds * length_beats)
        self.loop_active = True

    def clear_loop(self) -> None:
        self.loop_active = False

    def render_chunk(self, out_rate: int, frames: int) -> np.ndarray:
        if self.samples is None or not self.is_playing:
            return np.zeros((frames, 2), dtype=np.float32)

        source = self.samples
        ratio = (self.sample_rate / out_rate) * self.tempo
        idx = self.playhead + np.arange(frames) * ratio

        if self.loop_active:
            loop_start_idx = self.loop_start * self.sample_rate
            loop_end_idx = self.loop_end * self.sample_rate
            loop_len = max(1.0, loop_end_idx - loop_start_idx)
            idx = loop_start_idx + np.mod(idx - loop_start_idx, loop_len)

        max_idx = len(source) - 1
        clipped = np.clip(idx, 0, max_idx)
        i0 = np.floor(clipped).astype(int)
        i1 = np.minimum(i0 + 1, max_idx)
        frac = (clipped - i0)[:, None]
        out = source[i0] * (1 - frac) + source[i1] * frac

        self.playhead += frames * ratio
        if not self.loop_active and self.playhead >= max_idx:
            self.is_playing = False

        eq_gain = (self.eq_low + self.eq_mid + self.eq_high) / 3.0
        out *= self.gain * self.volume * eq_gain
        return out.astype(np.float32)
