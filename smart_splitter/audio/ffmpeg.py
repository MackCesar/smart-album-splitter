import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict


def probe_duration(src: str) -> float:
    if shutil.which("ffprobe") is None:
        raise RuntimeError("ffprobe not found in PATH (install FFmpeg)")
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=duration", "-of", "json", src
    ]
    out = subprocess.check_output(cmd)
    data = json.loads(out)
    dur = data["streams"][0].get("duration")
    return float(dur) if dur else 0.0


def cut_segments(*, src: str, tracks: List[Dict[str, str]], outdir: str, filename_template: str, codec: str) -> List[str]:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")
    out = []
    Path(outdir).mkdir(parents=True, exist_ok=True)
    ext = "m4a" if codec == "alac" else ("mp3" if codec == "mp3" else codec)

    for idx, t in enumerate(tracks, start=1):
        start = t["start"]
        end = t.get("end")
        title = t.get("title", f"Track {idx}")
        filename = filename_template.format(index=idx, title=_sanitize(title), ext=ext)
        dest = str(Path(outdir) / filename)

        args = ["ffmpeg", "-y", "-i", src, "-ss", start]
        if end:
            args += ["-to", end]
        if codec == "flac":
            args += ["-c:a", "flac"]
        elif codec == "mp3":
            args += ["-c:a", "libmp3lame", "-b:a", "320k"]
        elif codec == "alac":
            # Apple Lossless in an .m4a container
            args += ["-c:a", "alac"]
        else:  # wav
            args += ["-c:a", "pcm_s16le"]

        # Ensure proper extension and append destination
        if codec == "alac" and Path(dest).suffix.lower() != ".m4a":
            dest = str(Path(dest).with_suffix(".m4a"))

        # Quality-of-life for Apple players; safe no-op elsewhere
        if codec == "alac":
            args += ["-movflags", "+faststart"]

        # Append destination file path (REQUIRED)
        args += [dest]

        subprocess.run(args, check=True)
        out.append(dest)
    return out


def _sanitize(name: str) -> str:
    return "".join(c for c in name if c not in "\\/:*?\"<>|\n\r\t").strip()


def grab_snapshot(src: str, *, at: str, out: str):
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found in PATH")
    cmd = ["ffmpeg", "-y", "-ss", at, "-i", src, "-frames:v", "1", out]
    subprocess.run(cmd, check=True)
