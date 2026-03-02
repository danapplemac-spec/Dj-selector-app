from pathlib import Path

import numpy as np
import soundfile as sf

from library.scanner import extract_metadata, scan_audio_files


def test_scan_and_metadata(tmp_path: Path):
    sample = tmp_path / "tone.wav"
    sf.write(sample, np.zeros((44100, 2), dtype=np.float32), 44100)

    files = scan_audio_files(tmp_path)
    assert sample in files

    meta = extract_metadata(sample)
    assert meta["duration"] > 0.9
    assert meta["title"] == "tone"
