from pathlib import Path

from library.database import LibraryDB


def test_upsert_and_search(tmp_path: Path):
    db = LibraryDB(tmp_path / "lib.db")
    db.upsert_track({
        "path": "song.wav",
        "artist": "Artist",
        "title": "Title",
        "album": "Album",
        "genre": "House",
        "duration": 120,
        "bpm": 123.4,
        "musical_key": "A (11B)",
        "beatgrid_json": "[]",
        "waveform_json": "[]",
    })

    rows = db.list_tracks(search="Art")
    assert len(rows) == 1
    assert rows[0]["title"] == "Title"


def test_hotcues_persist(tmp_path: Path):
    db = LibraryDB(tmp_path / "lib.db")
    tid = db.upsert_track({
        "path": "song2.wav",
        "artist": "",
        "title": "Song2",
        "album": "",
        "genre": "",
        "duration": 180,
        "bpm": None,
        "musical_key": None,
        "beatgrid_json": None,
        "waveform_json": None,
    })
    db.set_hotcue(tid, 1, 42.0)
    assert db.get_hotcues(tid)[1] == 42.0
