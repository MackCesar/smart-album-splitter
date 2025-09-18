import typer
from pathlib import Path

from smart_splitter.core import run_pipeline, detect_only, split_only, tag_only

app = typer.Typer(help="Smart Album Splitter CLI")

@app.command()
def run(project: Path, force: bool = typer.Option(False), skip_download: bool = typer.Option(False)):
    """
    Run the full pipeline: download → detect tracklist → split → tag.
    """
    run_pipeline(str(project), force=force, skip_download=skip_download)

@app.command()
def detect(project: Path, emit: str = typer.Option("json", help="json|csv|cue"), out: Path = typer.Option(None)):
    """
    Detect timestamps from YouTube description/comments/transcript and print/export.
    """
    detect_only(str(project), emit=emit, out=out)

@app.command()
def split(project: Path):
    """Split audio using prepared tracklist."""
    split_only(str(project))

@app.command()
def tag(project: Path):
    """Reapply metadata & cover art."""
    tag_only(str(project))

if __name__ == "__main__":
    app()