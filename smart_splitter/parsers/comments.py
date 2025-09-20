from typing import List, Dict

from .timestamps import parse_timestamps

def extract_from_comments(comments: List[str]) -> List[Dict[str, str]]:
    """
    Parse a list of comment texts (e.g., top/pinned) for timestamps.
    Caller is responsible for fetching comments (yt-dlp, API, etc.).
    We simply aggregate and parse.
    """
    if not comments:
        return []
    blob = "\n".join(comments)
    return parse_timestamps(blob)