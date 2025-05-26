from __future__ import annotations

import heapq
from http.server import SimpleHTTPRequestHandler
import os
from functools import partial
import socketserver
import webbrowser
from pathlib import Path
from typing import List, Sequence, Optional

import typer
from rich.columns import Columns
from rich.console import Console

from slowpoke_finder.ab_reporting import build_ab_report_html
from slowpoke_finder.analyzer import deduplicate_avg
from slowpoke_finder.models import Step
from slowpoke_finder.registry import get as get_parser
from slowpoke_finder.utils import (
    generate_markdown_report,
    get_report_path,
    get_stats,
    print_rich_steps_table,
    make_rich_stats_table,
)

console = Console()
app = typer.Typer(no_args_is_help=True)


def collect_log_files(root: Path, patterns: Sequence[str]) -> list[Path]:
    """Gather files matching patterns under *root* (recursively)."""
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    return files


def parse_files(paths: list[Path], parser) -> list["Step"]:
    """Parse all files and aggregate steps (ignores unreadable files)."""
    steps: list["Step"] = []
    errors: list[tuple[Path, str]] = []
    for p in paths:
        try:
            steps.extend(parser.parse(str(p)))
        except Exception as exc:  # noqa: BLE001
            errors.append((p, str(exc)))
    if errors:
        console.print(f"[yellow]Skipped {len(errors)} file(s) due to parse errors[/]")
    return steps


@app.command()
def compare(
    run_a: str = typer.Argument(..., help="Path to log/dir for A"),
    run_b: str = typer.Argument(..., help="Path to log/dir for B"),
    format: str = typer.Option(..., "--format", "-f"),
    report_dir: str = typer.Option("ab-report", "--report-dir", help="Output folder"),
):
    """Generate an A/B HTML report comparing two runs."""
    parser = get_parser(format)

    paths_a = (
        collect_log_files(Path(run_a), ("*.json", "*.har"))
        if Path(run_a).is_dir()
        else [Path(run_a)]
    )
    paths_b = (
        collect_log_files(Path(run_b), ("*.json", "*.har"))
        if Path(run_b).is_dir()
        else [Path(run_b)]
    )

    steps_a = deduplicate_avg(parse_files(paths_a, parser))
    steps_b = deduplicate_avg(parse_files(paths_b, parser))

    build_ab_report_html(steps_a, steps_b, "A", "B", Path(report_dir))
    console.print(
        "Report is ready. To view it run:\n"
        f"[bold green]slowpoke-finder view-report {report_dir}[/bold green]"
    )


@app.command()
def view_report(report_path: str = typer.Argument(..., help="Path to report folder")):
    """Serve given report folder at http://localhost:8000/ for quick preview."""
    os.chdir(report_path)
    console.print("Serving on http://localhost:8000 (Ctrl+C to quit)")
    webbrowser.open("http://localhost:8000/index.html")

    handler = partial(SimpleHTTPRequestHandler, directory=".")
    with socketserver.TCPServer(("", 8000), handler) as httpd:  # type: ignore[arg-type]
        httpd.serve_forever()


@app.command()
def analyze(
    log: str = typer.Argument(..., help="Path to log file or folder"),
    format: str = typer.Option(
        ..., "--format", "-f", help="playwright | selenium | allure"
    ),
    top: int = typer.Option(
        5, "--top", "-n", help="Show N slowest steps after other filters"
    ),
    threshold: Optional[int] = typer.Option(
        None,
        "--threshold",
        "-t",
        help="Show steps slower than threshold (ms)",
    ),
    report: Optional[str] = typer.Option(
        None,
        "--report",
        "-r",
        help="Directory to save markdown report",
    ),
    percentiles: List[int] = typer.Option(
        (95, 99),
        "--percentiles",
        "-p",
        help="Extra percentiles: repeat flag, e.g. -p 50 -p 95 -p 99",
    ),
) -> None:
    """
    Parse Playwright / Selenium / Allure logs and print the slowest steps.

    Examples
    --------
    $ slowpoke-finder analyze ./allure-results -f allure -n 10
    $ slowpoke-finder analyze run.json -f playwright -t 500
    """
    log_path = Path(log)
    if log_path.is_dir():
        paths = collect_log_files(log_path, ("*.json", "*.har"))
        if not paths:
            console.print(f"[red]No *.json / *.har files in {log}[/]")
            raise typer.Exit(1)
    else:
        paths = [log_path]

    try:
        parser = get_parser(format)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(2)

    all_steps = parse_files(paths, parser)
    all_steps = deduplicate_avg(all_steps)

    if not all_steps:
        console.print("[red]No steps found[/]")
        raise typer.Exit(3)

    # Apply filters
    filtered = [s for s in all_steps if threshold is None or s.duration >= threshold]
    if not filtered:
        console.print(f"No steps ≥ {threshold} ms")
        raise typer.Exit(0)

    # Sort top N
    filtered = heapq.nlargest(top, filtered, key=lambda s: s.duration)

    # Render
    print_rich_steps_table(filtered, title="Slow steps")
    stats_filtered = get_stats(filtered, percentiles)
    stats_all = get_stats(all_steps, percentiles)
    table_filtered = make_rich_stats_table(stats_filtered, "Stats (filtered)")
    table_all = make_rich_stats_table(stats_all, "Stats (all)")
    console.print(Columns([table_filtered, table_all]))

    if report:
        report_path = get_report_path(report)
        report_path.write_text(
            generate_markdown_report(filtered, stats_filtered),
            encoding="utf-8",
        )
        console.print(f"Report saved → {report_path}")
