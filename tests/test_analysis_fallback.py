from api.controller import DJApiController


def test_analysis_error_event_when_optional_dependency_missing(tmp_path):
    api = DJApiController(tmp_path / "db.sqlite")
    api.db.upsert_track(
        {
            "path": "song.wav",
            "artist": "",
            "title": "Song",
            "album": "",
            "genre": "",
            "duration": 100,
            "bpm": None,
            "musical_key": None,
            "beatgrid_json": None,
            "waveform_json": None,
        }
    )

    seen = []
    api.on("onAnalysisError", lambda e: seen.append(e.payload))
    api.analyzeTrack("song.wav")
    assert seen, "Expected onAnalysisError when analysis deps are unavailable"
