"""
Builds a publishing schedule spread evenly across a chosen timeframe.
12 slots/day (every 2h) — slots already taken by other products are skipped.
Output: exact day + time (Italian) for each video + copy-paste caption.
"""
import math
from datetime import datetime, timedelta
from config.settings import PUBLISH_SLOTS_IT, SLOT_LABELS, PLATFORMS, VIDEOS_PER_DAY

MAX_DAYS = 28  # hard ceiling — generous enough for any timeframe


def build_schedule(
    videos: list[dict],
    start_date: datetime = None,
    occupied_slots: set[tuple[str, str]] = None,
    timeframe_days: int = 7,
) -> list[dict]:
    """
    Spread videos evenly across `timeframe_days` days, using free 2-hour slots.

    Args:
        videos:         List of video dicts from output_reader.
        start_date:     First day to consider (defaults to tomorrow).
        occupied_slots: Set of (date_it, time_it) pairs already used by
                        other keywords. Skipped during assignment.
        timeframe_days: Number of days to spread the schedule over.
                        The per-day cap is computed as ceil(len(videos) / timeframe_days),
                        so videos land on different days rather than piling up on day 1.
    Returns:
        List of scheduled item dicts, one per video.
    """
    if occupied_slots is None:
        occupied_slots = set()

    if start_date is None:
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

    # Distribute videos as evenly as possible across timeframe_days.
    # base_cap  = floor(N/D) — most days get this many
    # extra_cap = base_cap+1 — the first `n_extra` days get one more
    # This guarantees ALL videos land within exactly timeframe_days days.
    n_videos  = len(videos)
    base_cap  = max(1, n_videos // timeframe_days)
    n_extra   = n_videos % timeframe_days   # how many days get base_cap+1

    schedule  = []
    video_idx = 0
    day       = 0

    while video_idx < len(videos) and day < MAX_DAYS:
        current_date = start_date + timedelta(days=day)
        # First n_extra publishing days get one extra video to absorb the remainder
        daily_cap      = base_cap + (1 if day < n_extra else 0)
        assigned_today = 0  # videos assigned on this publishing day (resets each day)

        for slot_time in PUBLISH_SLOTS_IT:
            if video_idx >= len(videos):
                break
            if assigned_today >= daily_cap:
                break  # daily quota filled — move to next publishing day

            hour, minute = map(int, slot_time.split(":"))

            # Slots 01:00, 03:00, 05:00 cross midnight → next calendar day IT
            slot_date = current_date
            if hour < 7:
                slot_date = current_date + timedelta(days=1)

            publish_dt  = slot_date.replace(hour=hour, minute=minute)
            date_it_str = publish_dt.strftime("%A %d/%m/%Y")

            # Slot taken by another product — skip but keep looking on this day
            if (date_it_str, slot_time) in occupied_slots:
                continue

            video   = videos[video_idx]
            caption = video.get("caption", "")
            hook    = video.get("script", {}).get("hook", "")
            cta     = video.get("script", {}).get("cta", "")

            if not caption and hook:
                caption = f"{hook}\n\n{cta}\n\n#viralify #trending"

            schedule.append({
                "slot_number": video_idx + 1,
                "date_it":     date_it_str,
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

            assigned_today += 1
            video_idx += 1

        day += 1

    return schedule
