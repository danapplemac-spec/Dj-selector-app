from __future__ import annotations

from pathlib import Path

import soundfile as sf
from mutagen import File as MutagenFile

SUPPORTED_SUFFIXES = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff"}


def scan_audio_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def extract_metadata(path: Path) -> dict[str, str | float]:
    meta = MutagenFile(path)
    artist = title = album = genre = ""
    if meta and meta.tags:
        artist = str(meta.tags.get("TPE1", meta.tags.get("artist", [""]))[0]) if meta.tags.get("TPE1", meta.tags.get("artist")) else ""
        title = str(meta.tags.get("TIT2", meta.tags.get("title", [path.stem]))[0]) if meta.tags.get("TIT2", meta.tags.get("title")) else path.stem
        album = str(meta.tags.get("TALB", meta.tags.get("album", [""]))[0]) if meta.tags.get("TALB", meta.tags.get("album")) else ""
        genre = str(meta.tags.get("TCON", meta.tags.get("genre", [""]))[0]) if meta.tags.get("TCON", meta.tags.get("genre")) else ""
    info = sf.info(path)
    return {
        "path": str(path),
        "artist": artist,
        "title": title or path.stem,
        "album": album,
        "genre": genre,
        "duration": float(info.duration),
    }
