from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    artist TEXT,
    title TEXT,
    album TEXT,
    genre TEXT,
    duration REAL,
    bpm REAL,
    musical_key TEXT,
    beatgrid_json TEXT,
    waveform_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hotcues (
    id INTEGER PRIMARY KEY,
    track_id INTEGER NOT NULL,
    cue_index INTEGER NOT NULL,
    position_seconds REAL NOT NULL,
    UNIQUE(track_id, cue_index),
    FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS loops (
    id INTEGER PRIMARY KEY,
    track_id INTEGER NOT NULL,
    loop_index INTEGER NOT NULL,
    start_seconds REAL NOT NULL,
    length_beats INTEGER NOT NULL,
    UNIQUE(track_id, loop_index),
    FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
);
"""


class LibraryDB:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_track(self, track: dict[str, Any]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO tracks(path, artist, title, album, genre, duration, bpm, musical_key, beatgrid_json, waveform_json)
            VALUES(:path,:artist,:title,:album,:genre,:duration,:bpm,:musical_key,:beatgrid_json,:waveform_json)
            ON CONFLICT(path) DO UPDATE SET
                artist=excluded.artist,
                title=excluded.title,
                album=excluded.album,
                genre=excluded.genre,
                duration=excluded.duration,
                bpm=excluded.bpm,
                musical_key=excluded.musical_key,
                beatgrid_json=excluded.beatgrid_json,
                waveform_json=excluded.waveform_json
            """,
            track,
        )
        self.conn.commit()
        if cursor.lastrowid:
            return int(cursor.lastrowid)
        row = self.conn.execute("SELECT id FROM tracks WHERE path=?", (track["path"],)).fetchone()
        return int(row["id"])

    def list_tracks(self, search: str = "", sort_by: str = "title") -> list[dict[str, Any]]:
        sort_by = sort_by if sort_by in {"title", "artist", "duration", "bpm"} else "title"
        if search:
            rows = self.conn.execute(
                f"""
                SELECT * FROM tracks
                WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
                ORDER BY {sort_by} COLLATE NOCASE
                """,
                tuple(f"%{search}%" for _ in range(4)),
            ).fetchall()
        else:
            rows = self.conn.execute(
                f"SELECT * FROM tracks ORDER BY {sort_by} COLLATE NOCASE"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_track_by_path(self, path: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM tracks WHERE path=?", (path,)).fetchone()
        return dict(row) if row else None

    def set_hotcue(self, track_id: int, cue_index: int, position_seconds: float) -> None:
        self.conn.execute(
            """
            INSERT INTO hotcues(track_id, cue_index, position_seconds)
            VALUES(?,?,?)
            ON CONFLICT(track_id, cue_index) DO UPDATE SET position_seconds=excluded.position_seconds
            """,
            (track_id, cue_index, position_seconds),
        )
        self.conn.commit()

    def get_hotcues(self, track_id: int) -> dict[int, float]:
        rows = self.conn.execute(
            "SELECT cue_index, position_seconds FROM hotcues WHERE track_id=?", (track_id,)
        ).fetchall()
        return {int(row[0]): float(row[1]) for row in rows}

    def set_loop(self, track_id: int, loop_index: int, start_seconds: float, length_beats: int) -> None:
        self.conn.execute(
            """
            INSERT INTO loops(track_id, loop_index, start_seconds, length_beats)
            VALUES(?,?,?,?)
            ON CONFLICT(track_id, loop_index) DO UPDATE SET
                start_seconds=excluded.start_seconds,
                length_beats=excluded.length_beats
            """,
            (track_id, loop_index, start_seconds, length_beats),
        )
        self.conn.commit()

    def get_loops(self, track_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT loop_index, start_seconds, length_beats FROM loops WHERE track_id=? ORDER BY loop_index",
            (track_id,),
        ).fetchall()
        return [dict(row) for row in rows]
