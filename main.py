"""
viralify-ops — Main entry point

Commands (keyword is selected interactively if not passed):
  python main.py --schedule               # interactive keyword picker + video count prompt
  python main.py --metrics                # interactive keyword picker
  python main.py --decision               # interactive keyword picker
  python main.py --dashboard              # all keywords on SSD
  python main.py --compare                # interactive multi-keyword picker
"""
import argparse
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt

console = Console()


def select_keyword(prompt_text: str = "Select a keyword") -> str | None:
    """
    Show numbered list of keywords available on the SSD and let the user pick one.
    Returns the selected keyword, or None if nothing is available.
    """
    from src.reader.output_reader import list_available_keywords

    console.print()
    keywords = list_available_keywords()

    if not keywords:
        console.print("[red]No product folders found on SSD.[/red]")
        return None

    if len(keywords) == 1:
        console.print(f"[cyan]Auto-selected:[/cyan] {keywords[0]}\n")
        return keywords[0]

    console.print(f"[bold]{prompt_text}:[/bold]")
    for i, kw in enumerate(keywords, 1):
        console.print(f"  [{i}] {kw}")

    choice = IntPrompt.ask(
        "\nEnter number",
        default=1,
    )
    choice = max(1, min(choice, len(keywords)))
    selected = keywords[choice - 1]
    console.print(f"[cyan]Selected:[/cyan] {selected}\n")
    return selected


def select_keywords_multi(prompt_text: str = "Select keywords to compare") -> list[str]:
    """
    Let the user pick multiple keywords from the SSD list.
    Returns list of selected keywords.
    """
    from src.reader.output_reader import list_available_keywords

    console.print()
    keywords = list_available_keywords()

    if not keywords:
        console.print("[red]No product folders found on SSD.[/red]")
        return []

    console.print(f"[bold]{prompt_text}[/bold] (comma-separated numbers, e.g. 1,3):")
    for i, kw in enumerate(keywords, 1):
        console.print(f"  [{i}] {kw}")

    raw = Prompt.ask("\nEnter numbers", default="1")
    selected = []
    for part in raw.split(","):
        try:
            idx = int(part.strip())
            if 1 <= idx <= len(keywords):
                selected.append(keywords[idx - 1])
        except ValueError:
            pass

    if not selected:
        console.print("[yellow]No valid selection — using all keywords.[/yellow]")
        return keywords

    console.print(f"[cyan]Selected:[/cyan] {', '.join(selected)}\n")
    return selected


def cmd_schedule(keyword: str):
    import math  # used for cap_display computation below
    from src.reader.output_reader import get_keyword_outputs
    from src.scheduler.schedule_builder import build_schedule
    from src.scheduler.schedule_exporter import (
        export_csv, export_html_checklist, load_occupied_slots
    )

    console.print(f"\n[bold blue]Schedule builder —[/bold blue] {keyword}")
    videos = get_keyword_outputs(keyword)

    if not videos:
        console.print("[red]No videos found. Check SSD path and keyword folder.[/red]")
        return

    total_available = len(videos)
    console.print(f"\n[bold]{total_available} videos found[/bold] in [cyan]{keyword}[/cyan] output folder.")

    # 1 — How many videos to include
    n = IntPrompt.ask(
        "How many videos to schedule?",
        default=total_available,
    )
    n = max(1, min(n, total_available))
    if n < total_available:
        videos = videos[:n]
        console.print(f"[yellow]Using first {n} of {total_available} videos.[/yellow]")

    # 2 — Over how many days to spread them
    n_days = IntPrompt.ask(
        "Spread over how many days?",
        default=7,
    )
    n_days   = max(1, min(n_days, 28))
    base_cap = max(1, n // n_days)
    n_extra  = n % n_days
    cap_display = (
        f"{base_cap}-{base_cap + 1} video/day"
        if n_extra else
        f"{base_cap} video/day"
    )
    console.print(
        f"[cyan]Timeframe:[/cyan] {n_days} days — "
        f"[cyan]{cap_display}[/cyan] (evenly spread across different time slots)"
    )

    # 3 — Conflict check with other products
    occupied = load_occupied_slots(exclude_keyword=keyword)
    if occupied:
        console.print(
            f"[yellow]Found {len(occupied)} occupied slot(s) from other products — "
            f"conflicts will be skipped automatically.[/yellow]"
        )

    schedule  = build_schedule(videos, occupied_slots=occupied, timeframe_days=n_days)
    csv_path  = export_csv(schedule, keyword)
    html_path = export_html_checklist(schedule, keyword)

    # Compute actual date range used
    dates = [r["date_it"] for r in schedule]
    date_range = f"{dates[0]}  →  {dates[-1]}" if dates else "—"

    console.print(Panel.fit(
        f"[bold green]Schedule ready — {len(schedule)} videos across {n_days} days[/bold green]\n\n"
        f"Period : {date_range}\n"
        f"Cap    : {cap_display}  |  Slots: every 2h across the full day\n\n"
        f"CSV  : {csv_path}\n"
        f"HTML : {html_path}\n\n"
        f"Opening checklist in browser...\n"
        f"Schedule each video manually in Metricool at the listed times.",
        border_style="green"
    ))

    webbrowser.open(html_path.as_uri())


def cmd_metrics(keyword: str):
    from src.tracker.metrics_input import batch_input
    batch_input(keyword)


def cmd_decision(keyword: str):
    from src.decision.decision_engine import evaluate_product
    evaluate_product(keyword, show_summary=True)


def cmd_dashboard(keywords: list[str] = None):
    from src.reader.output_reader import list_available_keywords
    from src.report.report_builder import build_dashboard

    if not keywords:
        keywords = list_available_keywords()
    if not keywords:
        console.print("[yellow]No products found on SSD.[/yellow]")
        return

    report_path = build_dashboard(keywords)
    console.print(f"[green]✓ Dashboard updated:[/green] {report_path}")
    console.print("Open in browser to view.")


def cmd_compare(keywords: list[str]):
    from src.decision.decision_engine import compare_products
    compare_products(keywords)


def main():
    parser = argparse.ArgumentParser(description="viralify-ops — Content scheduling & analytics")
    parser.add_argument("--schedule",  action="store_true", help="Build publishing schedule")
    parser.add_argument("--metrics",   action="store_true", help="Enter video metrics")
    parser.add_argument("--decision",  action="store_true", help="Show go/kill decision")
    parser.add_argument("--dashboard", action="store_true", help="Update HTML dashboard (all keywords)")
    parser.add_argument("--compare",   action="store_true", help="Compare products side by side")
    # --keyword / --keywords are optional: interactive picker is used when omitted
    parser.add_argument("--keyword",   type=str, default="", help="Product keyword (optional — picked interactively if omitted)")
    parser.add_argument("--keywords",  nargs="+",           help="Multiple keywords for --compare (optional)")
    args = parser.parse_args()

    if args.schedule:
        keyword = args.keyword or select_keyword("Select keyword to schedule")
        if keyword:
            cmd_schedule(keyword)

    elif args.metrics:
        keyword = args.keyword or select_keyword("Select keyword to enter metrics for")
        if keyword:
            cmd_metrics(keyword)

    elif args.decision:
        keyword = args.keyword or select_keyword("Select keyword to evaluate")
        if keyword:
            cmd_decision(keyword)

    elif args.dashboard:
        cmd_dashboard(args.keywords)

    elif args.compare:
        keywords = args.keywords or select_keywords_multi("Select keywords to compare")
        if keywords:
            cmd_compare(keywords)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
