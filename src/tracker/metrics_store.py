"""
Local JSON database for metrics.
One file per keyword: data/metrics/[keyword].json
"""
import json
from pathlib import Path
from config.settings import DATA_DIR

METRICS_DIR = DATA_DIR / "metrics"


def _path(keyword: str) -> Path:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    return METRICS_DIR / f"{keyword.replace(' ', '_')}.json"


def save_metrics(keyword: str, entry: dict):
    path = _path(keyword)
    data = load_metrics(keyword)
    # Update if slot already exists, else append
    for i, existing in enumerate(data):
        if (existing["slot_number"] == entry["slot_number"] and
                existing["platform"] == entry["platform"]):
            data[i] = entry
            break
    else:
        data.append(entry)

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_metrics(keyword: str) -> list[dict]:
    path = _path(keyword)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def get_summary(keyword: str) -> dict:
    """Aggregate metrics across all videos for a keyword."""
    data = load_metrics(keyword)
    if not data:
        return {}

    total_views    = sum(e["views"]    for e in data)
    total_likes    = sum(e["likes"]    for e in data)
    total_comments = sum(e["comments"] for e in data)
    total_shares   = sum(e["shares"]   for e in data)
    total_saves    = sum(e["saves"]    for e in data)
    n_videos       = len(data)

    avg_er = sum(e["er"] for e in data) / n_videos if n_videos else 0
    best   = max(data, key=lambda x: x["er"]) if data else {}
    worst  = min(data, key=lambda x: x["er"]) if data else {}

    return {
        "keyword":        keyword,
        "n_videos":       n_videos,
        "total_views":    total_views,
        "total_likes":    total_likes,
        "total_comments": total_comments,
        "total_shares":   total_shares,
        "total_saves":    total_saves,
        "avg_er":         round(avg_er, 2),
        "best_er":        best.get("er", 0),
        "worst_er":       worst.get("er", 0),
        "best_video":     best.get("slot_number"),
        "platforms":      list(set(e["platform"] for e in data)),
    }
