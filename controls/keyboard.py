from __future__ import annotations

KEYMAP = {
    "space": ("togglePlay", {"deck": "A"}),
    "Return": ("togglePlay", {"deck": "B"}),
    "z": ("cue", {"deck": "A"}),
    "m": ("cue", {"deck": "B"}),
    "s": ("sync", {"target": "A", "source": "B"}),
    "k": ("sync", {"target": "B", "source": "A"}),
}
