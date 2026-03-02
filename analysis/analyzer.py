from __future__ import annotations

import json
from pathlib import Path

import librosa
import numpy as np


KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CAM_MAP = {
    "C": "8B", "C#": "3B", "D": "10B", "D#": "5B", "E": "12B", "F": "7B",
    "F#": "2B", "G": "9B", "G#": "4B", "A": "11B", "A#": "6B", "B": "1B",
}


def analyze_track(path: Path) -> dict[str, str | float]:
    y, sr = librosa.load(path, sr=None, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    downbeat = float(librosa.times_like(onset_env, sr=sr)[int(np.argmax(onset_env[: max(1, len(onset_env)//8)]))])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_idx = int(np.argmax(np.mean(chroma, axis=1)))
    key_name = KEYS[key_idx]
    camelot = CAM_MAP.get(key_name, "?")

    beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
    waveform = librosa.util.normalize(y)[:: max(1, len(y) // 5000)].tolist()

    return {
        "bpm": float(tempo),
        "beatgrid_json": json.dumps(beat_times),
        "waveform_json": json.dumps(waveform),
        "musical_key": f"{key_name} ({camelot})",
        "downbeat": downbeat,
    }
