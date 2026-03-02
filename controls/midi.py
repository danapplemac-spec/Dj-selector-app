from __future__ import annotations

from collections.abc import Callable


def start_midi_listener(dispatch: Callable[[str, dict], None]) -> None:
    try:
        import mido
    except Exception:
        return

    names = mido.get_input_names()
    if not names:
        return

    port = mido.open_input(names[0])

    def _on_message(msg):
        if msg.type == "note_on" and msg.note == 60:
            dispatch("togglePlay", {"deck": "A"})
        elif msg.type == "note_on" and msg.note == 62:
            dispatch("togglePlay", {"deck": "B"})

    port.callback = _on_message
