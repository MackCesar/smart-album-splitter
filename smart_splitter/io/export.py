from pathlib import Path
from typing import List, Dict


def export_cue(project, tracks: List[Dict[str, str]]):
    cue = Path(project.dir) / "album.cue"
    lines = [f"FILE \"{project.source_audio_path().name}\" WAVE"]
    for i, t in enumerate(tracks, start=1):
        title = t.get("title", f"Track {i}")
        mm, ss = _to_mm_ss(t["start"])  # cue is mm:ss:ff (frames), we leave ff as 00
        lines += [
            f"  TRACK {i:02d} AUDIO",
            f"    TITLE \"{title}\"",
            f"    INDEX 01 {mm:02d}:{ss:02d}:00",
        ]
    cue.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _to_mm_ss(hhmmss: str):
    hh, mm, ss = [int(x) for x in hhmmss.split(":")]
    total = hh * 60 + mm
    return total, ss