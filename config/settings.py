import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

SSD_DRIVE = os.getenv("SSD_DRIVE", "D")
SSD_BASE  = Path(f"{SSD_DRIVE}:\\Product Reels")

HANDLES = {
    "instagram": os.getenv("INSTAGRAM_HANDLE", "@viralify.xyz"),
    "tiktok":    os.getenv("TIKTOK_HANDLE",    "@viralify.xyz"),
    "youtube":   os.getenv("YOUTUBE_HANDLE",   "@viralifxyz"),
}

ER_GREEN   = float(os.getenv("ER_GREEN",  3.0))
ER_YELLOW  = float(os.getenv("ER_YELLOW", 1.5))
MIN_VIDEOS = int(os.getenv("MIN_VIDEOS_FOR_DECISION", 7))

# Publishing slots — Italian time (HH:MM)
PUBLISH_SLOTS_IT = ["13:00", "17:00", "21:00", "01:00", "04:00"]

# Slot labels for display
SLOT_LABELS = {
    "13:00": "US Morning  (07:00 EST / 12:00 GMT)",
    "17:00": "US Lunch    (11:00 EST / 16:00 GMT)",
    "21:00": "US Afternoon(15:00 EST / 20:00 GMT)",
    "01:00": "US Prime    (19:00 EST / 00:00 GMT)",  # next day IT
    "04:00": "AU Morning  (22:00 EST / 03:00 GMT)",  # next day IT
}

# Platforms to post on
PLATFORMS = ["TikTok", "Instagram", "YouTube Shorts"]
