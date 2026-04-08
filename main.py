"""
viralify-ops — Main entry point

Commands:
  python main.py --schedule  --keyword "wireless earbuds"   # build publishing schedule
  python main.py --metrics   --keyword "wireless earbuds"   # enter video metrics
  python main.py --decision  --keyword "wireless earbuds"   # show go/kill decision
  python main.py --dashboard                                 # update HTML dashboard
  python main.py --compare   --keywords "kw1" "kw2"        # compare products
"""
import argparse
from rich.console import Console
from rich.panel import Panel

console = Console()


def cmd_schedule(keyword: str):
    from src.reader.output_reader import get_keyword_outputs
    from src.scheduler.schedule_builder import build_schedule
    from src.scheduler.schedule_exporter import export_csv, export_html_checklist

    console.print(f"\n[bold blue]Building schedule for:[/bold blue] {keyword}")
    videos = get_keyword_outputs(keyword)

    if not videos:
        console.print("[red]No videos found. Check SSD path and keyword folder.[/red]")
        return

    schedule  = build_schedule(videos)
    csv_path  = export_csv(schedule, keyword)
    html_path = export_html_checklist(schedule, keyword)

    console.print(Panel.fit(
        f"[bold green]Schedule ready — {len(schedule)} slots over 7 days[/bold green]\n\n"
        f"CSV:  {csv_path}\n"
        f"HTML: {html_path}\n\n"
        f"Open the HTML checklist in your browser.\n"
        f"Schedule each video manually in Metricool at the listed times.",
        border_style="green"
    ))


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
    parser.add_argument("--dashboard", action="store_true", help="Update HTML dashboard")
    parser.add_argument("--compare",   action="store_true", help="Compare products")
    parser.add_argument("--keyword",   type=str, default="", help="Product keyword")
    parser.add_argument("--keywords",  nargs="+",           help="Multiple keywords (for --compare)")
    args = parser.parse_args()

    if args.schedule:
        if not args.keyword:
            console.print("[red]--keyword required[/red]")
            return
        cmd_schedule(args.keyword)

    elif args.metrics:
        if not args.keyword:
            console.print("[red]--keyword required[/red]")
            return
        cmd_metrics(args.keyword)

    elif args.decision:
        if not args.keyword:
            console.print("[red]--keyword required[/red]")
            return
        cmd_decision(args.keyword)

    elif args.dashboard:
        cmd_dashboard(args.keywords)

    elif args.compare:
        if not args.keywords:
            console.print("[red]--keywords required[/red]")
            return
        cmd_compare(args.keywords)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
