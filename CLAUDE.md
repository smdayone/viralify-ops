# CLAUDE.md — viralify-ops

## Project
Publishing scheduler, metrics tracker, and go/kill decision engine
for @viralify.xyz organic content testing.

## OS: Windows 11

## Workflow
1. Run dropship-radar → find candidate product
2. Run reels-factory → generate videos
3. Run viralify-ops --schedule → get publishing checklist
4. Post manually in Metricool using the HTML checklist
5. After each day: run viralify-ops --metrics → enter stats
6. Run viralify-ops --decision → GREEN/YELLOW/RED

## Key commands
```powershell
# Generate 7-day schedule
python main.py --schedule --keyword "wireless earbuds"

# Enter metrics after posting
python main.py --metrics --keyword "wireless earbuds"

# Check decision
python main.py --decision --keyword "wireless earbuds"

# Update dashboard
python main.py --dashboard

# Compare two products
python main.py --compare --keywords "wireless earbuds" "smart watch"
```

## Decision thresholds
GREEN  >= 3.0% ER  → continue + boost with ads
YELLOW  1.5-2.9%   → optimize hook
RED    < 1.5%      → kill, next product

## ER formula
ER = (likes + comments + shares + saves×2) / views × 100
Saves weighted 2x — strongest purchase intent signal.

## No API dependencies
Metricool scheduling is manual.
Metrics are entered manually via CLI.
No external API calls.
