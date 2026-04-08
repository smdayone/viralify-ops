"""
Reads video output folders from SSD.
Each output folder contains: final.mp4 + post_metadata.json
"""
import json
from pathlib import Path
from config.settings import SSD_BASE
from rich.console import Console

console = Console()


def get_keyword_outputs(keyword: str) -> list[dict]:
    """
    Scan D:\\Product Reels\\[keyword]\\output\\ for ready videos.
    Returns list of video dicts sorted by creation date.
    """
    output_dir = SSD_BASE / keyword / "output"

    if not output_dir.exists():
        console.print(f"[red]Output folder not found: {output_dir}[/red]")
        return []

    videos = []
    for session_dir in sorted(output_dir.iterdir()):
        if not session_dir.is_dir():
            continue

        video_path = session_dir / "final.mp4"
        meta_path  = session_dir / "post_metadata.json"

        if not video_path.exists():
            continue

        metadata = {}
        if meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        videos.append({
            "session":    session_dir.name,
            "video_path": str(video_path),
            "metadata":   metadata,
            "caption":    metadata.get("post_caption", ""),
            "product":    metadata.get("product", keyword),
            "keyword":    keyword,
            "script":     metadata.get("script", {}),
            "ready":      True,
        })

    console.print(f"[green]Found {len(videos)} videos for: {keyword}[/green]")
    return videos


def list_available_keywords() -> list[str]:
    """List all keywords that have output videos ready."""
    if not SSD_BASE.exists():
        console.print(f"[red]SSD not found at: {SSD_BASE}[/red]")
        return []

    keywords = []
    for kw_dir in sorted(SSD_BASE.iterdir()):
        if not kw_dir.is_dir():
            continue
        output_dir = kw_dir / "output"
        if output_dir.exists():
            count = sum(
                1 for d in output_dir.iterdir()
                if d.is_dir() and (d / "final.mp4").exists()
            )
            if count > 0:
                keywords.append(kw_dir.name)
                console.print(f"  [cyan]{kw_dir.name}[/cyan]: {count} videos ready")

    return keywords
