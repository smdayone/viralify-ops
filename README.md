# viralify-ops

Publishing scheduler, metrics tracker, and go/kill decision engine for [@viralify.xyz](https://instagram.com/viralify.xyz) organic short-form content testing.

## What it does

- Reads video output from SSD (`D:\Products Reels\[keyword]\output\`)
- Lets you pick the product interactively from a numbered list (no need to type keywords)
- Builds a publishing schedule spread evenly across a chosen timeframe (default 7 days)
- Supports **multiple products in parallel** — conflict detection prevents double-booking the same slot
- Exports a CSV + interactive HTML checklist (checkbox states persist across browser refreshes)
- Opens the checklist automatically in the browser after scheduling
- Tracks engagement metrics via CLI input
- Outputs a GREEN / YELLOW / RED go/kill decision per product
- Generates an HTML dashboard comparing all active products

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your SSD drive letter and account handles.

## Usage

All commands show an **interactive keyword picker** if `--keyword` is omitted.

```powershell
# Build publishing schedule (interactive: pick product, n° videos, timeframe)
python main.py --schedule

# Enter engagement metrics after posting
python main.py --metrics

# Show go/kill decision for a product
python main.py --decision

# Update HTML dashboard (all products on SSD)
python main.py --dashboard

# Compare multiple products side by side
python main.py --compare
```

You can still pass `--keyword` directly to skip the picker:

```powershell
python main.py --schedule --keyword "wireless earbuds"
```

## Scheduling logic

### Slot pool — 12 slots/day, every 2 hours (Italian time)

| IT time | EST | GMT | Market |
|---------|-----|-----|--------|
| 07:00 | 01:00 | 06:00 | AU prime / US late night |
| 09:00 | 03:00 | 08:00 | UK morning |
| 11:00 | 05:00 | 10:00 | UK late morning |
| 13:00 | 07:00 | 12:00 | US morning commute |
| 15:00 | 09:00 | 14:00 | US mid-morning |
| 17:00 | 11:00 | 16:00 | US lunch / UK after work |
| 19:00 | 13:00 | 18:00 | US early afternoon |
| 21:00 | 15:00 | 20:00 | US afternoon / UK evening |
| 23:00 | 17:00 | 22:00 | US prime evening |
| 01:00 | 19:00 | 00:00 | US prime time |
| 03:00 | 21:00 | 02:00 | US late night / AU early |
| 05:00 | 23:00 | 04:00 | AU morning |

### Multi-product parallel testing

With 12 slots/day and 3 videos/day per product, up to **4 products** can run in parallel on the same days without any slot overlap. When scheduling a new product the system automatically reads all existing schedule CSVs and skips occupied slots.

Example — 3 products, 7-day timeframe, same start date:

| Day | Product A | Product B | Product C |
|-----|-----------|-----------|-----------|
| Mon | 07 · 09 · 11 | 13 · 15 · 17 | 19 · 21 · 23 |
| Tue | 07 · 09 · 11 | 13 · 15 · 17 | 19 · 21 · 23 |
| … | … | … | … |

### Even spread across chosen timeframe

Videos are distributed as evenly as possible across the selected number of days:

- 15 videos / 7 days → 1 day with 3 videos + 6 days with 2 videos
- 21 videos / 7 days → 7 days with 3 videos each
- 10 videos / 7 days → 3 days with 2 videos + 4 days with 1 video

## Decision framework

| Signal | ER threshold | Action |
|--------|-------------|--------|
| GREEN | ≥ 3.0% | Scale up — boost best video with €100 ads |
| YELLOW | 1.5–2.9% | Optimize hook / format |
| RED | < 1.5% | Kill — move to next product |

Minimum 7 videos posted for a reliable decision.

**ER formula:** `(likes + comments + shares + saves×2) / views × 100`
Saves weighted 2× — strongest purchase-intent signal.

## Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SSD_DRIVE` | `D` | Drive letter of the SSD |
| `INSTAGRAM_HANDLE` | `@viralify.xyz` | Display handle |
| `TIKTOK_HANDLE` | `@viralify.xyz` | Display handle |
| `YOUTUBE_HANDLE` | `@viralifxyz` | Display handle |
| `ER_GREEN` | `3.0` | Green threshold (%) |
| `ER_YELLOW` | `1.5` | Yellow threshold (%) |
| `MIN_VIDEOS_FOR_DECISION` | `7` | Min videos before deciding |
| `VIDEOS_PER_DAY` | `3` | Fallback cap (overridden by timeframe) |
