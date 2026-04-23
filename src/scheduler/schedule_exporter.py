"""
Export schedule as:
1. CSV — importable into spreadsheets
2. HTML checklist — open in browser, check off as you post

Files are written with fixed names (no timestamp) and overwritten on each run.
Schedule rows are sorted ascending by datetime (next to post at the top).
Checkbox states persist across browser refreshes via localStorage.
"""
import csv
from pathlib import Path
from datetime import datetime
from config.settings import DATA_DIR

SCHEDULES_DIR = DATA_DIR / "schedules"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sort_key(item: dict) -> datetime:
    """Parse date_it + time_it into a datetime for ascending sort."""
    # date_it format: "Thursday 09/04/2026"  →  extract "09/04/2026"
    date_part = item["date_it"].split(" ", 1)[1]
    return datetime.strptime(f"{date_part} {item['time_it']}", "%d/%m/%Y %H:%M")


def load_occupied_slots(exclude_keyword: str) -> set[tuple[str, str]]:
    """
    Scan all schedule_*.csv files in SCHEDULES_DIR.
    Skip the file(s) that belong to exclude_keyword.
    Return a set of (date_it, time_it) pairs already used by other products.
    """
    occupied: set[tuple[str, str]] = set()
    slug    = exclude_keyword.replace(" ", "_")
    pattern = f"schedule_{slug}"          # matches both old (timestamped) and new names

    if not SCHEDULES_DIR.exists():
        return occupied

    for csv_file in SCHEDULES_DIR.glob("schedule_*.csv"):
        if pattern in csv_file.name:      # skip current keyword's file(s)
            continue
        try:
            with open(csv_file, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    d = row.get("date_it", "").strip()
                    t = row.get("time_it", "").strip()
                    if d and t:
                        occupied.add((d, t))
        except Exception:
            continue                       # corrupt / unreadable file — skip silently

    return occupied


# ---------------------------------------------------------------------------
# Exporters
# ---------------------------------------------------------------------------

def export_csv(schedule: list[dict], keyword: str) -> Path:
    """Export schedule to CSV (fixed filename, overwrites previous)."""
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = SCHEDULES_DIR / f"schedule_{keyword.replace(' ', '_')}.csv"

    # Sort ascending so the next slot to post is always at the top
    sorted_schedule = sorted(schedule, key=_sort_key)

    fields = [
        "slot_number", "date_it", "time_it", "slot_label",
        "product", "caption", "video_path", "status"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted_schedule)

    return csv_path


def export_html_checklist(schedule: list[dict], keyword: str) -> Path:
    """Export as interactive HTML checklist (fixed filename, overwrites previous).

    Checkbox states persist across page refreshes via localStorage.
    A generation ID is embedded in the page so that regenerating the schedule
    automatically clears stale checkbox states.
    """
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)
    html_path = SCHEDULES_DIR / f"checklist_{keyword.replace(' ', '_')}.html"

    # Sort ascending — next to post at the top
    sorted_schedule = sorted(schedule, key=_sort_key)

    # Generation ID: changes whenever the schedule content changes.
    # Old localStorage keys (from a previous run) are simply ignored.
    keyword_slug  = keyword.replace(" ", "_")
    first         = sorted_schedule[0]
    first_slot_id = f"{first['date_it'].replace(' ', '_')}_{first['time_it']}"
    gen_id        = f"viralify_{keyword_slug}_{len(sorted_schedule)}_{first_slot_id}"

    rows = ""
    for item in sorted_schedule:
        caption_escaped = item["caption"].replace('"', "&quot;").replace("\n", "<br>")
        platforms       = ", ".join(item["platforms"])
        num             = item["slot_number"]
        rows += f"""
<tr id="row-{num}">
  <td><input type="checkbox" data-num="{num}" onchange="markDone(this, {num})"></td>
  <td><strong>#{num}</strong></td>
  <td>{item['date_it']}</td>
  <td><span class="time">{item['time_it']}</span><br>
      <small>{item['slot_label']}</small></td>
  <td>{item['product']}</td>
  <td><small>{caption_escaped}</small></td>
  <td><code style="font-size:10px;word-break:break-all">{item['video_path']}</code></td>
  <td>{platforms}</td>
</tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Publishing Checklist — {keyword}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, sans-serif; background: #0f0f0f;
       color: #f0f0f0; padding: 24px; }}
h1 {{ color: #0A84FF; margin-bottom: 4px; }}
.meta {{ color: #666; font-size: 13px; margin-bottom: 24px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
th {{ background: #1e1e1e; padding: 10px 8px; text-align: left;
     color: #0A84FF; border-bottom: 2px solid #333; }}
td {{ padding: 10px 8px; border-bottom: 1px solid #222; vertical-align: top; }}
tr.done td {{ opacity: 0.4; text-decoration: line-through; }}
.time {{ font-size: 18px; font-weight: 700; color: #64D2FF; }}
input[type=checkbox] {{ width: 18px; height: 18px; cursor: pointer; }}
.progress {{ background: #1e1e1e; border-radius: 8px; padding: 16px;
             margin-bottom: 24px; display: flex; gap: 32px; }}
.stat {{ text-align: center; }}
.stat-num {{ font-size: 28px; font-weight: 700; color: #0A84FF; }}
.stat-label {{ font-size: 12px; color: #666; }}
</style>
</head>
<body>
<h1>Publishing Checklist</h1>
<p class="meta">Product: <strong>{keyword}</strong> —
Generated: {datetime.now().strftime("%d/%m/%Y %H:%M")} —
{len(sorted_schedule)} videos scheduled</p>

<div class="progress">
  <div class="stat">
    <div class="stat-num" id="posted-count">0</div>
    <div class="stat-label">Posted</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(sorted_schedule)}</div>
    <div class="stat-label">Total</div>
  </div>
  <div class="stat">
    <div class="stat-num" id="remaining-count">{len(sorted_schedule)}</div>
    <div class="stat-label">Remaining</div>
  </div>
</div>

<table>
<thead>
<tr>
  <th>&#10003;</th><th>#</th><th>Date (IT)</th><th>Time (IT)</th>
  <th>Product</th><th>Caption</th><th>Video File</th><th>Platforms</th>
</tr>
</thead>
<tbody>{rows}</tbody>
</table>

<script>
const TOTAL = {len(sorted_schedule)};
const GEN   = "{gen_id}";

function markDone(cb, num) {{
  const row = document.getElementById('row-' + num);
  if (cb.checked) {{
    row.classList.add('done');
    localStorage.setItem(GEN + '_slot_' + num, '1');
  }} else {{
    row.classList.remove('done');
    localStorage.removeItem(GEN + '_slot_' + num);
  }}
  recalculate();
}}

function recalculate() {{
  let posted = 0;
  document.querySelectorAll('input[type=checkbox]').forEach(function(cb) {{
    if (cb.checked) posted++;
  }});
  document.getElementById('posted-count').textContent = posted;
  document.getElementById('remaining-count').textContent = TOTAL - posted;
}}

document.addEventListener('DOMContentLoaded', function() {{
  // Restore saved checkbox states for this schedule generation
  document.querySelectorAll('input[type=checkbox]').forEach(function(cb) {{
    const num = cb.getAttribute('data-num');
    if (localStorage.getItem(GEN + '_slot_' + num) === '1') {{
      cb.checked = true;
      document.getElementById('row-' + num).classList.add('done');
    }}
  }});
  recalculate();
}});
</script>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")
    return html_path
