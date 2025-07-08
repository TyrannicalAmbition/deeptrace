from __future__ import annotations
import heapq
from pathlib import Path
from typing import List, Optional

import typer
from rich.columns import Columns
from rich.console import Console

from deeptrace.core.analyzer import deduplicate_avg
from deeptrace.core.parsers.parser_manager import autodetect_parser
from deeptrace.utils import (
    generate_markdown_report,
    get_report_path,
    get_stats,
    make_rich_stats_table,
    print_rich_steps_table,
)

console = Console()


def analyze(
    log: Path = typer.Argument(
        ..., dir_okay=True, exists=True, help="Файл лога или директория allure-results"
    ),
    top: int = typer.Option(5, "--top", "-n", help="Показать N самых долгих шагов"),
    threshold: Optional[int] = typer.Option(
        None, "--threshold", "-t", help="Фильтр по минимальной длительности, ms"
    ),
    report: Optional[Path] = typer.Option(
        None, "--report", "-r", help="Директория для сохранения отчёта .md"
    ),
    percentiles: List[int] = typer.Option(
        (95, 99), "--percentiles", "-p", help="Доп. перцентили, напр. -p 90 -p 99"
    ),
):
    console.print("[yellow]Detecting log format...[/]")
    fmt, steps = autodetect_parser(log)
    if not fmt:
        console.print("[red]Failed to detect format[/]")
        raise typer.Exit(1)

    console.print(f"[green]Detected format: {fmt}[/]")

    steps = deduplicate_avg(steps)
    if threshold is not None:
        steps = [s for s in steps if s.duration >= threshold]
    if not steps:
        console.print("No steps match given threshold")
        raise typer.Exit()

    slowest = heapq.nlargest(top, steps, key=lambda s: s.duration)

    print_rich_steps_table(slowest)
    stats_all = get_stats(steps, percentiles)
    stats_slow = get_stats(slowest, percentiles)

    console.print(
        Columns(
            [
                make_rich_stats_table(stats_slow, "Stats (filtered)"),
                make_rich_stats_table(stats_all, "Stats (all)"),
            ]
        )
    )

    if report:
        path = get_report_path(report)
        path.write_text(generate_markdown_report(slowest, stats_slow), encoding="utf-8")
        console.print(f"Report saved → {path}")
