"""
Export schedule as:
1. CSV — importable into spreadsheets
2. HTML checklist — open in browser, check off as you post
"""
import csv
from pathlib import Path
from datetime import datetime
from config.settings import DATA_DIR

SCHEDULES_DIR = DATA_DIR / "schedules"


def export_csv(schedule: list[dict], keyword: str) -> Path:
    """Export schedule to CSV."""
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    csv_path = SCHEDULES_DIR / f"schedule_{keyword.replace(' ', '_')}_{date_str}.csv"

    fields = [
        "slot_number", "date_it", "time_it", "slot_label",
        "product", "caption", "video_path", "status"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(schedule)

    return csv_path


def export_html_checklist(schedule: list[dict], keyword: str) -> Path:
    """Export as interactive HTML checklist."""
    SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    html_path = SCHEDULES_DIR / f"checklist_{keyword.replace(' ', '_')}_{date_str}.html"

    rows = ""
    for item in schedule:
        caption_escaped = item["caption"].replace('"', "&quot;").replace("\n", "<br>")
        platforms = ", ".join(item["platforms"])
        rows += f"""
<tr id="row-{item['slot_number']}">
  <td><input type="checkbox" onchange="markDone(this, {item['slot_number']})"></td>
  <td><strong>#{item['slot_number']}</strong></td>
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
{len(schedule)} videos over 7 days</p>

<div class="progress">
  <div class="stat">
    <div class="stat-num" id="posted-count">0</div>
    <div class="stat-label">Posted</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(schedule)}</div>
    <div class="stat-label">Total</div>
  </div>
  <div class="stat">
    <div class="stat-num" id="remaining-count">{len(schedule)}</div>
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
let posted = 0;
const total = {len(schedule)};
function markDone(cb, num) {{
  const row = document.getElementById('row-' + num);
  if (cb.checked) {{
    row.classList.add('done');
    posted++;
  }} else {{
    row.classList.remove('done');
    posted--;
  }}
  document.getElementById('posted-count').textContent = posted;
  document.getElementById('remaining-count').textContent = total - posted;
}}
</script>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")
    return html_path
