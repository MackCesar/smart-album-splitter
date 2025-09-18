import re
from typing import List, Dict

# Matches 00:00, 0:30, 1:02:45
TIMESTAMP_PATTERN = re.compile(r"(?P<hours>\d{1,2}:)?(?P<minutes>[0-5]?\d):(?P<seconds>[0-5]?\d)")


def normalize_hms(h: int, m: int, s: int) -> str:
    total = h * 3600 + m * 60 + s
    hh = total // 3600
    mm = (total % 3600) // 60
    ss = total % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def parse_timestamps(text: str) -> List[Dict[str, str]]:
    """Parse lines with timestamps → normalized HH:MM:SS + title."""
    tracks: List[Dict[str, str]] = []
    for line in text.splitlines():
        m = TIMESTAMP_PATTERN.search(line)
        if not m:
            continue
        hours = int(m.group("hours")[:-1]) if m.group("hours") else 0
        minutes = int(m.group("minutes"))
        seconds = int(m.group("seconds"))
        ts = normalize_hms(hours, minutes, seconds)
        title = line.replace(m.group(0), "").strip(" -–—:|\t[](){}") or f"Track {len(tracks)+1}"
        tracks.append({"start": ts, "title": title})
    return tracks