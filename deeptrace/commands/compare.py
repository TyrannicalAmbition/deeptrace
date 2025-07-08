from __future__ import annotations
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from deeptrace.core.analyzer import deduplicate_avg
from deeptrace.core.parsers.parser_manager import autodetect_parser
from deeptrace.utils import (
    generate_ab_markdown_report,
    get_report_path,
    get_stats,
    print_rich_ab_comparison,
)

console = Console()


def compare(
    run_a: Path = typer.Argument(..., exists=True, help="Лог/директория A"),
    run_b: Path = typer.Argument(..., exists=True, help="Лог/директория B"),
    report: Optional[Path] = typer.Option(
        None, "--report", "-r", help="Директория для сохранения отчёта .md"
    ),
):
    for label, p in (("A", run_a), ("B", run_b)):
        if not p.exists():
            console.print(f"[red]{label} path does not exist[/]")
            raise typer.Exit(1)

    console.print("[yellow]Detecting format for A...[/]")
    fmt_a, steps_a = autodetect_parser(run_a)
    console.print("[yellow]Detecting format for B...[/]")
    fmt_b, steps_b = autodetect_parser(run_b)

    if not fmt_a or not fmt_b:
        console.print("[red]Could not detect format[/]")
        raise typer.Exit(1)
    if fmt_a != fmt_b:
        console.print(f"[red]Format mismatch: A={fmt_a}, B={fmt_b}[/]")
        raise typer.Exit(1)

    console.print(f"[green]Detected format: {fmt_a}[/]")

    steps_a = deduplicate_avg(steps_a)
    steps_b = deduplicate_avg(steps_b)
    stats_a, stats_b = get_stats(steps_a), get_stats(steps_b)

    if report:
        path = get_report_path(report)
        md = generate_ab_markdown_report(steps_a, steps_b, stats_a, stats_b)
        path.write_text(md, encoding="utf-8")
        console.print(f"Report saved → {path}")
    else:
        print_rich_ab_comparison(steps_a, steps_b, stats_a, stats_b)
