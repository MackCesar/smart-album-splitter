from typing import List, Dict
from smart_splitter.parsers.timestamps import parse_timestamps


def extract_from_description(description: str) -> List[Dict[str, str]]:
    """Extract tracklist from a YouTube description string."""
    if not description:
        return []
    return parse_timestamps(description)