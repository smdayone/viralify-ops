# viralify-ops

Publishing scheduler, metrics tracker, and go/kill decision engine for [@viralify.xyz](https://instagram.com/viralify.xyz) organic content testing.

## What it does

- Reads video output from SSD (`D:\Product Reels\[keyword]\output\`)
- Generates a 7-day manual publishing schedule with exact times (Italian timezone)
- Exports an interactive HTML checklist for Metricool scheduling
- Tracks engagement metrics via CLI input
- Outputs a GREEN / YELLOW / RED decision per product

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and verify your SSD drive letter.

## Usage

```powershell
# Generate 7-day publishing schedule
python main.py --schedule --keyword "wireless earbuds"

# Enter metrics after posting
python main.py --metrics --keyword "wireless earbuds"

# Check go/kill decision
python main.py --decision --keyword "wireless earbuds"

# Update HTML dashboard (all products)
python main.py --dashboard

# Compare multiple products
python main.py --compare --keywords "wireless earbuds" "smart watch"
```

## Decision framework

| Signal  | ER threshold | Action                        |
|---------|-------------|-------------------------------|
| GREEN   | ≥ 3.0%      | Scale up, boost with €100 ads |
| YELLOW  | 1.5–2.9%    | Optimize hook / format        |
| RED     | < 1.5%      | Kill, move to next product    |

Minimum 7 videos posted for a reliable decision.

**ER formula:** `(likes + comments + shares + saves×2) / views × 100`
Saves are weighted 2× — strongest purchase intent signal.

## Publishing schedule

5 slots/day targeting US/UK/AU audiences (times in Italian timezone):

| Slot | IT time | Target market         |
|------|---------|-----------------------|
| 1    | 13:00   | US morning commute    |
| 2    | 17:00   | US lunch break        |
| 3    | 21:00   | US afternoon / UK eve |
| 4    | 01:00   | US prime time         |
| 5    | 04:00   | US late night / AU am |
