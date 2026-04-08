"""
Decision engine: GREEN / YELLOW / RED per product.
Based on average ER across all posted videos.
"""
from rich.console import Console
from rich.panel import Panel
from config.settings import ER_GREEN, ER_YELLOW, MIN_VIDEOS
from src.tracker.metrics_store import load_metrics, get_summary

console = Console()


def evaluate_product(keyword: str, show_summary: bool = True) -> str:
    """
    Returns 'green', 'yellow', or 'red'.
    Also prints recommendation if show_summary=True.
    """
    metrics = load_metrics(keyword)
    n = len(metrics)

    if n == 0:
        if show_summary:
            console.print(f"[yellow]No metrics recorded for: {keyword}[/yellow]")
        return "no_data"

    summary = get_summary(keyword)
    avg_er  = summary["avg_er"]

    if avg_er >= ER_GREEN:
        decision = "green"
        color    = "green"
        action   = "CONTINUE — Scale up. Boost best video with €100 ads."
        next_step = (
            f"Best video: #{summary['best_video']} (ER {summary['best_er']}%)\n"
            f"→ Create product page on Viralify\n"
            f"→ Boost video #{summary['best_video']} with €100 Meta/TikTok ads\n"
            f"→ Keep posting 5 videos/day"
        )
    elif avg_er >= ER_YELLOW:
        decision = "yellow"
        color    = "yellow"
        action   = "OPTIMIZE — Change hook or video format."
        next_step = (
            f"Average ER {avg_er}% — below target but not dead.\n"
            f"→ Review worst-performing videos — identify pattern\n"
            f"→ Change hook style for next 5 videos\n"
            f"→ Try different clip order (lead with solution instead of problem)"
        )
    else:
        decision = "red"
        color    = "red"
        action   = "KILL — Move to next product."
        next_step = (
            f"Average ER {avg_er}% — audience not interested.\n"
            f"→ Stop scheduling videos for this product\n"
            f"→ Archive content — do not delete\n"
            f"→ Run dropship-radar to find next candidate"
        )

    if show_summary:
        progress_bar = "█" * min(n, MIN_VIDEOS) + "░" * max(0, MIN_VIDEOS - n)
        data_note = (
            "" if n >= MIN_VIDEOS
            else f"  [yellow]⚠ Only {n}/{MIN_VIDEOS} videos posted — decision may change[/yellow]\n"
        )

        panel = Panel.fit(
            f"[bold]Product:[/bold] {keyword}\n"
            f"[bold]Videos posted:[/bold] {n}  [{progress_bar}] {n}/{MIN_VIDEOS} min\n"
            f"{data_note}"
            f"\n[bold]Avg ER:[/bold] [{color}]{avg_er}%[/{color}]  "
            f"(Best: {summary['best_er']}% / Worst: {summary['worst_er']}%)\n"
            f"[bold]Views:[/bold] {summary['total_views']:,}  "
            f"[bold]Saves:[/bold] {summary['total_saves']:,}\n"
            f"\n[bold {color}]{action}[/bold {color}]\n\n"
            f"{next_step}",
            title=f"[bold {color}]● {decision.upper()}[/bold {color}]",
            border_style=color,
        )
        console.print(panel)

    return decision


def compare_products(keywords: list[str]) -> None:
    """Compare multiple products side by side."""
    from rich.table import Table

    table = Table(title="Product Comparison", show_lines=True)
    table.add_column("Product",  style="cyan")
    table.add_column("Videos",   justify="center")
    table.add_column("Avg ER",   justify="center")
    table.add_column("Best ER",  justify="center")
    table.add_column("Views",    justify="right")
    table.add_column("Decision", justify="center")

    for kw in keywords:
        summary  = get_summary(kw)
        if not summary:
            table.add_row(kw, "-", "-", "-", "-", "[yellow]NO DATA[/yellow]")
            continue
        decision = evaluate_product(kw, show_summary=False)
        colors   = {"green": "green", "yellow": "yellow", "red": "red"}
        color    = colors.get(decision, "white")
        table.add_row(
            kw,
            str(summary["n_videos"]),
            f"[{color}]{summary['avg_er']}%[/{color}]",
            f"{summary['best_er']}%",
            f"{summary['total_views']:,}",
            f"[bold {color}]{decision.upper()}[/bold {color}]",
        )

    console.print(table)
