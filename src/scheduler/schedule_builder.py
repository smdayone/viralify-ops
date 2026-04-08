"""
Builds a 7-day manual publishing schedule.
Output: exact day + time (Italian) for each video + copy-paste caption.
"""
from datetime import datetime, timedelta
from config.settings import PUBLISH_SLOTS_IT, SLOT_LABELS, PLATFORMS


def build_schedule(videos: list[dict], start_date: datetime = None) -> list[dict]:
    """
    Assign each video to a publishing slot over 7 days.
    5 slots/day × 7 days = 35 slots max.
    Returns list of scheduled items.
    """
    if start_date is None:
        # Start from tomorrow at first slot
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    schedule = []
    video_idx = 0
    day = 0

    while video_idx < len(videos) and day < 7:
        current_date = start_date + timedelta(days=day)

        for slot_time in PUBLISH_SLOTS_IT:
            if video_idx >= len(videos):
                break

            video = videos[video_idx]
            hour, minute = map(int, slot_time.split(":"))

            # Handle slots that cross midnight (01:00, 04:00 are next calendar day)
            slot_date = current_date
            if hour < 8:  # early morning slots belong to next day
                slot_date = current_date + timedelta(days=1)

            publish_dt = slot_date.replace(hour=hour, minute=minute)

            caption = video.get("caption", "")
            hook = video.get("script", {}).get("hook", "")
            cta  = video.get("script", {}).get("cta", "")

            # Build full caption if not already in metadata
            if not caption and hook:
                caption = f"{hook}\n\n{cta}\n\n#viralify #trending"

            schedule.append({
                "slot_number": video_idx + 1,
                "date_it":     publish_dt.strftime("%A %d/%m/%Y"),
                "time_it":     slot_time,
                "slot_label":  SLOT_LABELS.get(slot_time, ""),
                "day_number":  day + 1,
                "video_path":  video["video_path"],
                "session":     video["session"],
                "product":     video["product"],
                "keyword":     video["keyword"],
                "caption":     caption,
                "platforms":   PLATFORMS,
                "status":      "pending",  # pending / posted / skipped
            })

            video_idx += 1

        day += 1

    return schedule
