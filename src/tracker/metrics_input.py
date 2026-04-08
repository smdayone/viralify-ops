"""
CLI to manually input metrics for each posted video.
Run after checking Metricool / platform analytics.
"""
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from src.tracker.metrics_store import save_metrics, load_metrics
from src.decision.decision_engine import evaluate_product

console = Console()


def input_video_metrics(keyword: str, slot_number: int):
    """Interactive CLI to enter metrics for one video."""
    console.print(f"\n[bold blue]Metrics Input[/bold blue] — {keyword} / Video #{slot_number}")
    console.print("Enter 0 if the video hasn't been posted yet.\n")

    views    = IntPrompt.ask("  Views")
    likes    = IntPrompt.ask("  Likes")
    comments = IntPrompt.ask("  Comments")
    shares   = IntPrompt.ask("  Shares")
    saves    = IntPrompt.ask("  Saves")
    platform = Prompt.ask("  Platform", choices=["TikTok", "Instagram", "YouTube"], default="TikTok")

    if views == 0:
        console.print("[yellow]  Skipped — no data entered.[/yellow]")
        return

    # ER calculation (saves weighted 2x)
    er = ((likes + comments + shares + (saves * 2)) / views) * 100

    entry = {
        "keyword":     keyword,
        "slot_number": slot_number,
        "platform":    platform,
        "views":       views,
        "likes":       likes,
        "comments":    comments,
        "shares":      shares,
        "saves":       saves,
        "er":          round(er, 2),
        "recorded_at": datetime.now().isoformat(),
    }

    save_metrics(keyword, entry)

    console.print(f"\n  [bold]ER: [cyan]{er:.2f}%[/cyan][/bold]")
    if er >= 3.0:
        console.print("  [green]→ GREEN — good engagement[/green]")
    elif er >= 1.5:
        console.print("  [yellow]→ YELLOW — optimize hook or format[/yellow]")
    else:
        console.print("  [red]→ RED — low engagement[/red]")


def batch_input(keyword: str):
    """Enter metrics for multiple videos in sequence."""
    console.print(f"\n[bold]Batch metrics input for: {keyword}[/bold]")
    console.print("Enter metrics for each posted video. Press Ctrl+C to stop.\n")

    existing   = load_metrics(keyword)
    start_from = max((e["slot_number"] for e in existing), default=0) + 1

    try:
        slot = start_from
        while True:
            input_video_metrics(keyword, slot)
            slot += 1
            cont = Prompt.ask("\nEnter next video?", choices=["y", "n"], default="y")
            if cont == "n":
                break
    except KeyboardInterrupt:
        pass

    # Show current decision
    console.print("\n")
    evaluate_product(keyword, show_summary=True)
