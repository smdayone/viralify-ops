"""
HTML dashboard — updated on every run.
Shows all products being tested, metrics, and decisions.
"""
from datetime import datetime
from pathlib import Path
from config.settings import DATA_DIR, ER_GREEN, ER_YELLOW
from src.tracker.metrics_store import load_metrics, get_summary
from src.decision.decision_engine import evaluate_product

REPORTS_DIR = DATA_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "dashboard.html"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #0f0f0f;
       color: #f0f0f0; padding: 32px; }
h1 { color: #0A84FF; font-size: 28px; margin-bottom: 4px; }
.meta { color: #666; font-size: 12px; margin-bottom: 32px; }
.thresholds { background: #1e1e1e; border-radius: 8px; padding: 12px 16px;
              margin-bottom: 32px; font-size: 12px; display: flex; gap: 24px; }
.t-green { color: #30d158; } .t-yellow { color: #ffd60a; } .t-red { color: #ff453a; }

.product-card { background: #161616; border: 1px solid #2a2a2a;
  border-radius: 10px; margin-bottom: 24px; overflow: hidden; }
.product-card.green  { border-color: #30d158; }
.product-card.yellow { border-color: #ffd60a; }
.product-card.red    { border-color: #ff453a; }

.card-header { padding: 16px 20px; display: flex;
               justify-content: space-between; align-items: center; }
.card-title { font-size: 18px; font-weight: 700; }
.decision-badge { font-size: 12px; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
.badge-green  { background: #30d15822; color: #30d158; border: 1px solid #30d15844; }
.badge-yellow { background: #ffd60a22; color: #ffd60a; border: 1px solid #ffd60a44; }
.badge-red    { background: #ff453a22; color: #ff453a; border: 1px solid #ff453a44; }
.badge-nodata { background: #44444422; color: #888;    border: 1px solid #44444444; }

.stats-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1px;
              background: #2a2a2a; border-top: 1px solid #2a2a2a; }
.stat-box { background: #161616; padding: 14px; text-align: center; }
.stat-num { font-size: 22px; font-weight: 700; color: #f0f0f0; }
.stat-num.er-green  { color: #30d158; }
.stat-num.er-yellow { color: #ffd60a; }
.stat-num.er-red    { color: #ff453a; }
.stat-label { font-size: 11px; color: #666; margin-top: 2px; }

.action-box { padding: 14px 20px; border-top: 1px solid #2a2a2a;
              font-size: 13px; color: #aaa; }
.action-box strong { color: #f0f0f0; }

.video-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.video-table th { background: #1e1e1e; padding: 8px 12px; text-align: left; color: #666; }
.video-table td { padding: 8px 12px; border-bottom: 1px solid #1e1e1e; }
.videos-section { padding: 0 20px 20px; }
"""

JS = """
function toggleVideos(keyword) {
  const el = document.getElementById('videos-' + keyword.replace(/\\s/g,'_'));
  if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
"""


def build_dashboard(keywords: list[str]):
    """Build/update the HTML dashboard for all keywords."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    cards_html = ""
    for kw in keywords:
        summary  = get_summary(kw)
        decision = evaluate_product(kw, show_summary=False)
        metrics  = load_metrics(kw)

        badge_class = {
            "green":   "badge-green",
            "yellow":  "badge-yellow",
            "red":     "badge-red",
            "no_data": "badge-nodata",
        }.get(decision, "badge-nodata")

        badge_label = {
            "green":   "● CONTINUE",
            "yellow":  "● OPTIMIZE",
            "red":     "● KILL",
            "no_data": "○ NO DATA",
        }.get(decision, "○ NO DATA")

        if summary:
            avg_er = summary["avg_er"]
            er_class = (
                "er-green"  if avg_er >= ER_GREEN  else
                "er-yellow" if avg_er >= ER_YELLOW else
                "er-red"
            )
            stats = f"""
<div class="stats-grid">
  <div class="stat-box">
    <div class="stat-num {er_class}">{avg_er}%</div>
    <div class="stat-label">Avg ER</div>
  </div>
  <div class="stat-box">
    <div class="stat-num">{summary['n_videos']}</div>
    <div class="stat-label">Videos</div>
  </div>
  <div class="stat-box">
    <div class="stat-num">{summary['total_views']:,}</div>
    <div class="stat-label">Views</div>
  </div>
  <div class="stat-box">
    <div class="stat-num">{summary['total_likes']:,}</div>
    <div class="stat-label">Likes</div>
  </div>
  <div class="stat-box">
    <div class="stat-num">{summary['total_saves']:,}</div>
    <div class="stat-label">Saves ×2</div>
  </div>
  <div class="stat-box">
    <div class="stat-num">{summary['best_er']}%</div>
    <div class="stat-label">Best ER</div>
  </div>
</div>"""

            action = {
                "green":  f"→ Boost video #{summary.get('best_video')} with €100 ads. Create product page on Viralify.",
                "yellow": "→ Change hook style for next batch. Try leading with solution.",
                "red":    "→ Stop scheduling. Run dropship-radar for next product.",
            }.get(decision, "→ Post videos and enter metrics.")

            # Video table
            rows = ""
            for m in sorted(metrics, key=lambda x: x["slot_number"]):
                er_c = (
                    "color:#30d158" if m["er"] >= ER_GREEN  else
                    "color:#ffd60a" if m["er"] >= ER_YELLOW else
                    "color:#ff453a"
                )
                rows += f"""<tr>
  <td>#{m['slot_number']}</td>
  <td>{m['platform']}</td>
  <td>{m['views']:,}</td>
  <td>{m['likes']:,}</td>
  <td>{m['comments']:,}</td>
  <td>{m['shares']:,}</td>
  <td>{m['saves']:,}</td>
  <td style="{er_c};font-weight:700">{m['er']}%</td>
</tr>"""

            kw_id = kw.replace(" ", "_")
            videos_section = f"""
<div class="videos-section">
  <a href="#" onclick="toggleVideos('{kw}');return false"
     style="font-size:12px;color:#0A84FF">Show/hide video breakdown</a>
  <div id="videos-{kw_id}" style="display:none;margin-top:12px">
    <table class="video-table">
      <thead><tr>
        <th>#</th><th>Platform</th><th>Views</th><th>Likes</th>
        <th>Comments</th><th>Shares</th><th>Saves</th><th>ER</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>"""

        else:
            stats          = "<div style='padding:16px 20px;color:#666;font-size:13px'>No metrics entered yet.</div>"
            action         = "→ Post videos and enter metrics with: python main.py --metrics"
            videos_section = ""

        cards_html += f"""
<div class="product-card {decision}">
  <div class="card-header">
    <div class="card-title">{kw}</div>
    <div class="decision-badge {badge_class}">{badge_label}</div>
  </div>
  {stats}
  <div class="action-box"><strong>Next action:</strong> {action}</div>
  {videos_section}
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="300">
<title>viralify-ops Dashboard</title>
<style>{CSS}</style>
</head>
<body>
<h1>viralify-ops</h1>
<p class="meta">Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')} —
Auto-refreshes every 5 minutes</p>
<div class="thresholds">
  <span class="t-green">● GREEN: ER &ge; {ER_GREEN}% → Scale up + boost with ads</span>
  <span class="t-yellow">● YELLOW: ER {ER_YELLOW}-{ER_GREEN}% → Optimize hook/format</span>
  <span class="t-red">● RED: ER &lt; {ER_YELLOW}% → Kill, next product</span>
  <span style="color:#666">Min 7 videos for reliable decision</span>
</div>
{cards_html}
<script>{JS}</script>
</body>
</html>"""

    REPORT_PATH.write_text(html, encoding="utf-8")
    return REPORT_PATH
