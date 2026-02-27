from api.controller import DJApiController


def test_search_library(tmp_path):
    api = DJApiController(tmp_path / "db.sqlite")
    api.db.upsert_track({
        "path": "song.wav",
        "artist": "Daft Punk",
        "title": "One More Time",
        "album": "Discovery",
        "genre": "House",
        "duration": 100,
        "bpm": 123,
        "musical_key": "D (10B)",
        "beatgrid_json": "[]",
        "waveform_json": "[]",
    })
    assert len(api.searchLibrary("Daft")) == 1
