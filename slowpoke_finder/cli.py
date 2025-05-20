from __future__ import annotations

from pathlib import Path
import heapq
import typer
from slowpoke_finder.registry import get
from slowpoke_finder.utils import (
    print_steps_table,
    print_stats,
    generate_markdown_report,
    get_stats,
    get_report_path,
)

app = typer.Typer(no_args_is_help=True)


@app.command()
def analyze(
    log: str = typer.Argument(..., help="Path to log file or folder"),
    format: str = typer.Option(
        ..., "--format", "-f", help="playwright | selenium | allure"
    ),
    top: int = typer.Option(5, "--top", "-n", help="Show top N slow steps"),
    threshold: int = typer.Option(
        None, "--threshold", "-t", help="Show steps slower than threshold (ms)"
    ),
    report: str = typer.Option(
        None, "--report", "-r", help="Directory to save markdown report"
    ),
) -> None:
    """Analyze logs and print slow steps."""
    paths: list[Path]
    log_path = Path(log)
    if log_path.is_dir():
        paths = list(log_path.rglob("*.json")) + list(log_path.rglob("*.har"))
        if not paths:
            typer.echo(f"No *.json / *.har files in {log}", err=True)
            raise typer.Exit(1)
    else:
        paths = [log_path]

    try:
        parser = get(format)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)

    all_steps = []
    for p in paths:
        try:
            all_steps.extend(parser.parse(str(p)))
        except Exception as e:  # noqa: BLE001
            typer.echo(f"Parse error {p}: {e}", err=True)

    if not all_steps:
        typer.echo("No steps found", err=True)
        raise typer.Exit(1)

    if threshold is not None:
        steps_out = [s for s in all_steps if s.duration >= threshold]
        if not steps_out:
            typer.echo(f"No steps >= {threshold} ms")
            raise typer.Exit(0)
        title = f"Steps >= {threshold} ms"
    else:
        steps_out = heapq.nlargest(top, all_steps, key=lambda s: s.duration)
        title = f"Top {top} slowest steps"

    print_steps_table(steps_out, title=title)
    stats = get_stats(steps_out)
    print_stats(stats)

    if report:
        report_path = get_report_path(report)
        report_content = generate_markdown_report(steps_out, stats)
        report_path.write_text(report_content, encoding="utf-8")
        typer.echo(f"Report saved -> {report_path}")
