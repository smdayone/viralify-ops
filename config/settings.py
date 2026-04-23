import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

SSD_DRIVE = os.getenv("SSD_DRIVE", "D")
SSD_BASE  = Path(f"{SSD_DRIVE}:\\Products Reels")

HANDLES = {
    "instagram": os.getenv("INSTAGRAM_HANDLE", "@viralify.xyz"),
    "tiktok":    os.getenv("TIKTOK_HANDLE",    "@viralify.xyz"),
    "youtube":   os.getenv("YOUTUBE_HANDLE",   "@viralifxyz"),
}

ER_GREEN   = float(os.getenv("ER_GREEN",  3.0))
ER_YELLOW  = float(os.getenv("ER_YELLOW", 1.5))
MIN_VIDEOS = int(os.getenv("MIN_VIDEOS_FOR_DECISION", 7))

# Max videos assigned per product per calendar day.
# With 12 slots/day and 3 videos/day/product → up to 4 products can share the same day.
VIDEOS_PER_DAY = int(os.getenv("VIDEOS_PER_DAY", 3))

# Publishing slots — Italian time (HH:MM)
# 12 slots evenly spaced every 2 hours across a publishing "day".
# A publishing day runs 07:00 → 05:00 IT (next calendar day).
# Slots 01:00, 03:00, 05:00 fall on the next calendar day (hour < 7).
#
# Capacity: 12 slots/day supports up to 3 products tested in parallel
#           (each product fills ~4 slots/day, none ever conflicts).
PUBLISH_SLOTS_IT = [
    "07:00",  # AU prime / US late night    (01:00 EST / 06:00 GMT)
    "09:00",  # UK morning                  (03:00 EST / 08:00 GMT)
    "11:00",  # UK late morning             (05:00 EST / 10:00 GMT)
    "13:00",  # US morning commute          (07:00 EST / 12:00 GMT)
    "15:00",  # US mid-morning             (09:00 EST / 14:00 GMT)
    "17:00",  # US lunch / UK after work    (11:00 EST / 16:00 GMT)
    "19:00",  # US early afternoon          (13:00 EST / 18:00 GMT)
    "21:00",  # US afternoon / UK evening   (15:00 EST / 20:00 GMT)
    "23:00",  # US prime evening            (17:00 EST / 22:00 GMT)
    "01:00",  # US prime time              (19:00 EST / 00:00 GMT)  ← next calendar day IT
    "03:00",  # US late night / AU early   (21:00 EST / 02:00 GMT)  ← next calendar day IT
    "05:00",  # AU morning                 (23:00 EST / 04:00 GMT)  ← next calendar day IT
]

# Slot labels for display
SLOT_LABELS = {
    "07:00": "AU Prime / US Late     (01:00 EST / 06:00 GMT)",
    "09:00": "UK Morning             (03:00 EST / 08:00 GMT)",
    "11:00": "UK Late Morning        (05:00 EST / 10:00 GMT)",
    "13:00": "US Morning Commute     (07:00 EST / 12:00 GMT)",
    "15:00": "US Mid-Morning         (09:00 EST / 14:00 GMT)",
    "17:00": "US Lunch / UK After W. (11:00 EST / 16:00 GMT)",
    "19:00": "US Early Afternoon     (13:00 EST / 18:00 GMT)",
    "21:00": "US Afternoon / UK Eve  (15:00 EST / 20:00 GMT)",
    "23:00": "US Prime Evening       (17:00 EST / 22:00 GMT)",
    "01:00": "US Prime Time          (19:00 EST / 00:00 GMT)",
    "03:00": "US Late / AU Early     (21:00 EST / 02:00 GMT)",
    "05:00": "AU Morning             (23:00 EST / 04:00 GMT)",
}

# Platforms to post on
PLATFORMS = ["TikTok", "Instagram", "YouTube Shorts"]
