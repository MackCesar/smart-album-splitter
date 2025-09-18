from typing import List, Dict, Optional
from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.mp3 import EasyMP3


def apply_tags(files: List[str], album_meta: Dict, *, cover: Optional[str] = None) -> None:
    album = album_meta.get("album")
    album_artist = album_meta.get("album_artist") or album_meta.get("artist")
    year = str(album_meta.get("year")) if album_meta.get("year") else None
    genre = album_meta.get("genre")
    comment = album_meta.get("comment")

    cover_bytes = None
    cover_mime = None
    if cover and Path(cover).exists():
        cover_bytes = Path(cover).read_bytes()
        suffix = Path(cover).suffix.lower()
        cover_mime = "image/png" if suffix == ".png" else "image/jpeg"

    for idx, f in enumerate(files, start=1):
        p = Path(f)
        if p.suffix.lower() == ".flac":
            audio = FLAC(f)
            if album:
                audio["album"] = album
            if album_artist:
                audio["albumartist"] = album_artist
            audio["tracknumber"] = str(idx)
            if year:
                audio["date"] = year
            if genre:
                audio["genre"] = genre
            if comment:
                audio["comment"] = comment
            if cover_bytes:
                pic = Picture()
                pic.type = 3
                pic.mime = cover_mime or "image/jpeg"
                pic.desc = "Cover"
                pic.data = cover_bytes
                audio.clear_pictures()
                audio.add_picture(pic)
            audio.save()
        elif p.suffix.lower() == ".mp3":
            audio = EasyMP3(f)
            if album:
                audio["album"] = album
            if album_artist:
                audio["albumartist"] = album_artist
            audio["tracknumber"] = str(idx)
            if year:
                audio["date"] = year
            if genre:
                audio["genre"] = genre
            # EasyMP3 doesn't embed pictures; would need ID3 APIC via mutagen.id3 if desired
            audio.save()