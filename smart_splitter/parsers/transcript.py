from __future__ import annotations
from typing import List, Dict, Optional
import re
from pathlib import Path
from .timestamps import parse_timestamps

VTT_TS = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}")

def _read_vtt(vtt_path: Path) -> str:
    return vtt_path.read_text(encoding="utf-8", errors="ignore")

def extract_from_transcript(*, vtt_text:Optional[str] = None, vtt_path: Optional[str] = None) -> List[Dict[str, str]]:
    """Extract tracklist from a YouTube transcript file. If transcript has explicit timestamped titles"""
    text = vtt_text or (_read_vtt(Path(vtt_path)) if vtt_path else "")
    if not text:
        return []
    lines = []
    for line in text.splitlines():
        if VTT_TS.match(line) or line.strip().startswith(("WEBVTT","Kind:","Language")):
            continue
        lines.append(line)
        return parse_timestamps("\n".join(lines))