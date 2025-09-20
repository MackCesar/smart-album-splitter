from __future__ import annotations
import re
import shutil
import subprocess
from typing import List, Dict

SILENCE_OUT = re.compile(r"silence_start:\s*(?P<start>[0-9.]+)|silence_end:\s*(?P<end>[0-9.]+)")

def _run_silencedetect(src: str, noise_db: str = "-30dB", min_silence: float = 0.8) -> List[Dict[str, float]]:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed")
    cmd = [
        "ffmpeg","-i", src, "-af", f"silencedetect=noise[{noise_db}:d={min_silence}]",
        "-f","null", "-"
    ]

    p = subprocess.run(cmd, check=True, capture_output=True, text=True)
    spans = []
    cur = {}
    for line in (p.stderr or "").splitlines():
        m = SILENCE_OUT.match(line)
        if not m:
            continue
        if m.group("start"):
            cur = {"start": float(m.group("start"))}
        elif m.group("end") and cur:
            cur["end"] = float(m.group("end"))
            spans.append(cur)
            cur = {}
    return spans

def _sec_to_hms(s: float) -> str:
    s = int(s)
    hh = s // 3600
    mm = (s % 3600) // 60
    ss = s % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

def suggest_cuts_from_silence(src: str, *, min_gap: float = 1.5) -> List[Dict[str, float]]:
    """
    Suggest candidate 'start' timestamps at the ends of silences (silence_end)
    longer than min_gap. These are just hints to be merged with textual sources.
    """
    spans = _run_silencedetect(src)
    candidates = []
    for sp in spans:
        dur = sp.get("end", 0) - sp.get("start", 0)
        if dur >= min_gap and "end" in sp:
            candidates.append({"start": _sec_to_hms(sp["end"]), "title": "Candidate"})
    # de-dup consecutive similar candidates
    seen = set()
    deduped = []
    for c in candidates:
        if c["start"] in seen:
            continue
        seen.add(c["start"])
        deduped.append(c)
    return deduped