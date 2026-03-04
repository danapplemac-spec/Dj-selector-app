from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from api.controller import DJApiController
from controls.keyboard import KEYMAP
from controls.midi import start_midi_listener


class DJApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DJ Selector MVP")
        self.controller = DJApiController(Path("library.db"))
        self.audio_started = False
        if os.getenv("DJ_SKIP_AUDIO") != "1":
            self.controller.start_audio()
            self.audio_started = True
        self._build_ui()
        self._bind_keys()
        threading.Thread(target=start_midi_listener, args=(self.dispatch,), daemon=True).start()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(top, text="Scan Folder", command=self.scan_folder).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search = ttk.Entry(top, textvariable=self.search_var)
        search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        search.bind("<KeyRelease>", lambda _e: self.refresh_tracks())

        middle = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        middle.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        lib_frame = ttk.Frame(middle)
        self.track_list = tk.Listbox(lib_frame)
        self.track_list.pack(fill=tk.BOTH, expand=True)
        self.track_list.bind("<Double-Button-1>", self.load_selected_to_a)
        middle.add(lib_frame, weight=3)

        deck_frame = ttk.Frame(middle)
        middle.add(deck_frame, weight=2)

        self.deck_labels = {}
        for deck in ["A", "B"]:
            frame = ttk.LabelFrame(deck_frame, text=f"Deck {deck}")
            frame.pack(fill=tk.X, pady=6)
            label = ttk.Label(frame, text="No track")
            label.pack(fill=tk.X)
            self.deck_labels[deck] = label
            ttk.Button(frame, text="Load Selected", command=lambda d=deck: self.load_selected(d)).pack(fill=tk.X)
            ttk.Button(frame, text="Play/Pause", command=lambda d=deck: self.dispatch("togglePlay", {"deck": d})).pack(fill=tk.X)
            ttk.Button(frame, text="Cue", command=lambda d=deck: self.dispatch("cue", {"deck": d})).pack(fill=tk.X)
            ttk.Button(frame, text="Set Hotcue 1", command=lambda d=deck: self.dispatch("setHotcue", {"deck": d, "index": 1})).pack(fill=tk.X)
            ttk.Button(frame, text="Jump Hotcue 1", command=lambda d=deck: self.dispatch("jumpHotcue", {"deck": d, "index": 1})).pack(fill=tk.X)
            ttk.Button(frame, text="Loop 4", command=lambda d=deck: self.dispatch("setLoop", {"deck": d, "length_beats": 4})).pack(fill=tk.X)

        mix = ttk.LabelFrame(self.root, text="Mixer")
        mix.pack(fill=tk.X, padx=10, pady=5)
        self.cross = tk.DoubleVar(value=0.5)
        ttk.Scale(mix, from_=0, to=1, variable=self.cross, command=lambda v: self.dispatch("setCrossfader", {"value": float(v)})).pack(fill=tk.X)
        ttk.Button(mix, text="Sync A->B", command=lambda: self.dispatch("sync", {"target": "A", "source": "B"})).pack(side=tk.LEFT)
        ttk.Button(mix, text="Sync B->A", command=lambda: self.dispatch("sync", {"target": "B", "source": "A"})).pack(side=tk.LEFT)
        ttk.Button(mix, text="Start Rec", command=lambda: self.dispatch("startRecording", {})).pack(side=tk.LEFT)
        ttk.Button(mix, text="Stop Rec", command=lambda: self.dispatch("stopRecording", {"path": "recording.wav"})).pack(side=tk.LEFT)

        self.wave = tk.Canvas(self.root, height=100, bg="#111")
        self.wave.pack(fill=tk.X, padx=10, pady=8)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var).pack(fill=tk.X, padx=10, pady=(0, 8))

        self.controller.on("onTrackLoaded", self.on_track_loaded)
        self.controller.on("onAnalysisComplete", self.on_analysis_complete)
        self.controller.on("onAnalysisError", self.on_analysis_error)
        self.refresh_tracks()

    def _bind_keys(self) -> None:
        for key, (command, payload) in KEYMAP.items():
            self.root.bind(f"<{key}>", lambda _e, c=command, p=payload: self.dispatch(c, p))

    def dispatch(self, command: str, payload: dict) -> None:
        fn = getattr(self.controller, command)
        fn(**payload)

    def scan_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.controller.scanLibrary(folder)
            self.refresh_tracks()

    def refresh_tracks(self) -> None:
        self.track_list.delete(0, tk.END)
        items = self.controller.searchLibrary(self.search_var.get())
        self.paths = []
        for row in items:
            self.track_list.insert(tk.END, f"{row['artist']} - {row['title']}")
            self.paths.append(row["path"])

    def get_selected_path(self) -> str | None:
        selected = self.track_list.curselection()
        if not selected:
            return None
        return self.paths[selected[0]]

    def load_selected(self, deck: str) -> None:
        path = self.get_selected_path()
        if not path:
            return
        self.controller.loadTrack(deck, path)
        self.controller.analyzeTrack(path)
        self.draw_waveform(path)

    def load_selected_to_a(self, _event) -> None:
        self.load_selected("A")

    def draw_waveform(self, path: str) -> None:
        data = self.controller.getWaveform(path)
        if not data:
            return
        self.wave.delete("all")
        w = self.wave.winfo_width() or 800
        h = self.wave.winfo_height() or 100
        step = max(1, len(data) // w)
        pts = data[::step]
        for i, v in enumerate(pts):
            y = h / 2
            amp = v * (h / 2 - 2)
            self.wave.create_line(i, y - amp, i, y + amp, fill="#35c7ff")

    def on_track_loaded(self, event) -> None:
        self.deck_labels[event.payload["deck"]].config(text=Path(event.payload["path"]).name)
        self.status_var.set(
            f"Loaded {Path(event.payload['path']).name} on deck {event.payload['deck']}"
        )

    def on_analysis_complete(self, event) -> None:
        bpm = event.payload.get("bpm")
        key = event.payload.get("musicalKey", "?")
        if isinstance(bpm, (int, float)):
            self.status_var.set(f"Analysis done: BPM {bpm:.1f} | Key {key}")
        else:
            self.status_var.set("Analysis done")

    def on_analysis_error(self, event) -> None:
        self.status_var.set(
            f"Analysis unavailable: {event.payload.get('error', 'missing optional deps')}"
        )


def run() -> None:
    root = tk.Tk()
    app = DJApp(root)

    if os.getenv("DJ_APP_SMOKETEST") == "1":
        root.after(2000, root.destroy)

    def _shutdown() -> None:
        if app.audio_started:
            app.controller.stop_audio()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _shutdown)
    root.mainloop()


if __name__ == "__main__":
    run()
