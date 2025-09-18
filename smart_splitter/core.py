from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

import yaml

from smart_splitter.io.export import export_cue

try:
    from yt_dlp import YoutubeDL
except Exception:
    YoutubeDL = None

from smart_splitter.parsers.timestamps import parse_timestamps
from smart_splitter.parsers.descriptions import extract_from_description
from smart_splitter.io.files import ensure_dir, read_yaml, write_json, write_csv
from smart_splitter.audio.ffmpeg import (
    probe_duration,
    cut_segments,
    grab_snapshot
)
from smart_splitter.audio.tags import apply_tags

class Project:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project file not found: {self.project_path}")
        self.cfg = read_yaml(self.project_path)
        self.slug = self.cfg.get("slug") or self.project_path.parent.name
        self.dir = self.project_path.parent
        self.outdir = Path(self.cfg.get("output", {}).get("outdir", f"projects/{self.slug}/output")).resolve()
        ensure_dir(self.outdir)

    @property
    def url(self) -> str:
        return self.cfg.get("source", {}).get("url", "")

    @property
    def preferred_sources(self) -> List[str]:
        return self.cfg.get("source", {}).get("prefer", ["description", "comments", "transcript"])

    @property
    def fallback_silence(self) -> bool:
        return bool(self.cfg.get("source", {}).get("fallback_silence", True))

    @property
    def codec(self) -> str:
        return (self.cfg.get("output", {}).get("codec") or "flac").lower()

    @property
    def cover(self) -> Optional[str]:
        return self.cfg.get("output", {}).get("cover")

    @property
    def filename_template(self) -> str:
        return self.cfg.get("output", {}).get("filename_template", "{index:02d} - {title}.{ext}")

    @property
    def metadata(self) -> Dict:
        return self.cfg.get("metadata", {})

    def source_audio_path(self) -> Path:
        # Using .m4a as bestaudio default from yt-dlp
        return self.dir / "source.m4a"

    def tracklist_json_path(self) -> Path:
        return self.dir / "tracklist.json"

    def tracklist_csv_path(self) -> Path:
        return self.dir / "tracklist.csv"

# ------------------ Public functions used by CLI ------------------

def run_pipeline(project_file: str,*, force: bool = False, skip_download: bool = False):
    p = Project(project_file)

    if not skip_download:
        download_audio_and_info(p, force=force)

    tracks = resolve_tracklist(p)
    write_json(p.tracklist_json_path(), tracks)
    write_csv(p.tracklist_csv_path(), tracks)
    export_cue(p, tracks)

    out_files = cut_segments(
        src=str(p.source_audio_path()),
        tracks=tracks,
        outdir=str(p.outdir),
        filename_template=p.filename_template,
        codec=p.codec,
    )

    apply_tags(out_files, p.metadata, cover=p.cover)

def detect_only(project_file: str, *,emit: str = "json", out: Optional[str] = None):
    p = Project(project_file)
    tracks = resolve_tracklist(p)
    if emit == "json":
        data = json.dumps(tracks, indent=2)
    elif emit == "csv":
        data = "index,title,start,end\n" + "\n".join(
            f"{i+1},{track['title'].replace(',', '')},{track['start']},{track.get('end','')}"
            for i, track in enumerate(tracks)
        )
    elif emit == "cue":
        export_cue(p, tracks)
        data = (p.dir / "album.cue").read_text(encoding="utf-8")
    else:
        raise ValueError(f"unknown emit: {emit}")

    if out:
        Path(out).write_text(data, encoding="utf-8")
    else:
        print(data)

def split_only(project_file: str):
    p = Project(project_file)
    if not p.source_audio_path().exists():
        raise FileNotFoundError(f"Source audio file not found. Run 'run' or download the audio file")
    tracks = __load_tracklist(p)
    out_files = cut_segments(
        src=str(p.source_audio_path()),tracks=tracks, outdir=str(p.outdir), filename_template=p.filename_template, codec=p.codec
    )
    print("Wrote:")
    for f in out_files:
        print(" ·", f)

def tag_only(project_file: str):
    p = Project(project_file)
    out_files = sorted(Path(p.outdir).glob(f"*.{p.codec if p.codec != 'mp3' else 'mp3'}"))
    if not out_files:
        print("No files found")
        return
    apply_tags([str(f) for f in out_files], p.metadata, cover=p.cover)

def snapshot_frame(project_file: str, *, at: str, out: str):
    p = Project(project_file)
    grab_snapshot(str(p.source_audio_path()), at=at, out=out)

def normalize_audio(project_file: str, *, mode: str = "ebur128"):
    p = Project(project_file)
    for audio in sorted(p.outdir.glob("*.flac")) + sorted(p.outdir.glob("*.mp3")):
        out = audio.with_name(audio.stem + ".norm" + audio.suffix)
        if mode == "ebur128":
            cmd = [
                "ffmpeg", "-y", "-i", str(audio),
                "-filter:a", "loudnorm=I=-16:TP=-1.5:LRA=11",
                str(out)
            ]
            subprocess.run(cmd, check=True)


# -------------------- helpers --------------------

def download_audio_and_info(p: Project, *, force: bool = False):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")
    if YoutubeDL is None:
        raise RuntimeError("yt-dlp not installed. Add it to requirements and pip install.")

    if p.source_audio_path().exists() and not force:
        print("✔ audio exists — skipping download (use --force to redownload)")
        return

    ydl_opts = {
        "quiet": True,
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": str(p.dir / "source.%(ext)s"),
        "writesubtitles": False,
        "writeinfojson": True,
        "skip_download": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(p.url, download=True)
        # normalize filename to source.m4a if necessary
        downloaded = p.dir / f"source.{info.get('ext','m4a')}"
        target = p.source_audio_path()
        if downloaded != target and downloaded.exists():
            downloaded.rename(target)

    print("✔ downloaded:", target)


def resolve_tracklist(p: Project) -> List[Dict[str, str]]:
    # 1) config-provided tracklist wins
    cfg_tracks = p.cfg.get("tracklist")
    if cfg_tracks:
        tracks = normalize_track_ends(cfg_tracks, total_duration=probe_duration(str(p.source_audio_path())) if p.source_audio_path().exists() else None)
        return tracks

    # 2) attempt auto-extraction from description
    desc = extract_description_via_ytdlp(p.url)
    tracks = extract_from_description(desc)

    if not tracks:
        print("⚠ no timestamps found in description. (Comments/transcript parsing not implemented in MVP)")
        # Optionally: fallback to silencedetect later

    total = None
    if p.source_audio_path().exists():
        total = probe_duration(str(p.source_audio_path()))
    tracks = normalize_track_ends(tracks, total_duration=total)
    return tracks


def __load_tracklist(p: Project) -> List[Dict[str, str]]:
    if p.tracklist_json_path.exists():
        return json.loads(p.tracklist_json_path.read_text(encoding="utf-8"))
    raise FileNotFoundError("tracklist.json not found. Run detect or run first.")


def normalize_track_ends(tracks: List[Dict[str, str]], *, total_duration: Optional[float]) -> List[Dict[str, str]]:
    """Ensure each item has start and optional end. Fill the last end with total_duration if available."""
    def to_seconds(ts: str) -> int:
        hh, mm, ss = [int(x) for x in ts.split(":")]
        return hh * 3600 + mm * 60 + ss

    # sort by start
    tracks2 = sorted(tracks, key=lambda t: to_seconds(t["start"]))
    for i, t in enumerate(tracks2):
        if "end" not in t or not t["end"]:
            if i < len(tracks2) - 1:
                t["end"] = tracks2[i + 1]["start"]
            elif total_duration is not None:
                # format total as HH:MM:SS
                td = int(total_duration)
                hh = td // 3600
                mm = (td % 3600) // 60
                ss = td % 60
                t["end"] = f"{hh:02d}:{mm:02d}:{ss:02d}"
    # add titles if missing
    for idx, t in enumerate(tracks2, start=1):
        t.setdefault("title", f"Track {idx}")
    return tracks2


def extract_description_via_ytdlp(url: str) -> str:
    if YoutubeDL is None:
        return ""
    with YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("description", "") or ""