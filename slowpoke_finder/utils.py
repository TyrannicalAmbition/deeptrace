from __future__ import annotations

from pathlib import Path

from rich.columns import Columns
from rich.table import Table
from rich.console import Console
from statistics import mean, median
from typing import Iterable, List, Sequence, Tuple


__all__ = [
    "get_report_path",
    "get_stats",
    "generate_markdown_report",
    "generate_ab_markdown_report",
    "make_rich_stats_table",
    "print_rich_steps_table",
    "print_rich_ab_comparison",
]

from slowpoke_finder.models import Step


# ============================================================================
# File-system helpers
# ============================================================================


def get_report_path(report_dir: str | Path, fmt: str = "md") -> Path:
    """
    Ensures that *report_dir* exists and returns the full path
    ``<report_dir>/report.<fmt>``.

    Parameters
    ----------
    report_dir : str or Path
        Target directory where the report will be saved.
    fmt : str
        File extension to use (default: ``"md"``).

    Returns
    -------
    Path
        Full path to the report file.
    """
    dir_path = Path(report_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / f"report.{fmt}"


# ============================================================================
# Statistics
# ============================================================================


def _percentile(sorted_vals: list[int], p: int) -> int:
    """
    Calculates a simple linear-interpolated percentile (numpy-like).

    Assumes *sorted_vals* is **already** sorted in ascending order.

    Parameters
    ----------
    sorted_vals : list[int]
        List of sorted values.
    p : int
        Percentile to compute (0..100).

    Returns
    -------
    int
        The percentile value.
    """
    if not sorted_vals:
        return 0
    if p <= 0:
        return sorted_vals[0]
    if p >= 100:
        return sorted_vals[-1]

    k = (len(sorted_vals) - 1) * (p / 100)
    f, c = int(k), int(k) + 1
    if c >= len(sorted_vals):
        return sorted_vals[-1]
    return int(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def get_stats(
    steps: Iterable["Step"], percentiles: Sequence[int] = (95, 99)
) -> List[Tuple[str, str]]:
    """
    Calculate summary statistics for a set of steps.

    Returns a list of (metric, value) tuples ready for rendering.

    Parameters
    ----------
    steps : Iterable[Step]
        List or iterable of Step objects.
    percentiles : Sequence[int]
        Additional percentiles to include (default: 95, 99).

    Returns
    -------
    List[Tuple[str, str]]
        List of (metric, value) tuples.
    """
    durations: list[int] = [s.duration for s in steps]
    if not durations:
        return [
            ("Total steps", "0"),
            ("Min", "0 ms"),
            ("Max", "0 ms"),
            ("Median (p50)", "0 ms"),
            ("Avg", "0 ms"),
        ]

    durations.sort()
    stats: list[Tuple[str, str]] = [
        ("Total steps", str(len(durations))),
        ("Min", f"{durations[0]} ms"),
        ("Max", f"{durations[-1]} ms"),
        ("Median (p50)", f"{int(median(durations))} ms"),
        ("Avg", f"{mean(durations):.1f} ms"),
    ]

    for p in sorted(set(percentiles)):
        if p in (0, 50, 100):
            continue  # Already covered or not informative
        stats.append((f"P{p}", f"{_percentile(durations, p)} ms"))
    return stats


# ============================================================================
# Rendering helpers
# ============================================================================


def generate_markdown_report(
    steps: Iterable["Step"],
    stats: Sequence[Tuple[str, str]],
    title: str = "Slowpoke Finder Report",
) -> str:
    """
    Generate a Markdown report from a list of steps and statistics.

    Parameters
    ----------
    steps : Iterable[Step]
        List or iterable of Step objects.
    stats : Sequence[Tuple[str, str]]
        List of (metric, value) tuples.
    title : str
        The report title.

    Returns
    -------
    str
        Markdown report as a string.
    """
    lines: list[str] = [f"# {title}", ""]

    steps = list(steps)
    if not steps:
        return "\n".join(lines + ["_No steps found._"])

    # Steps table
    lines += [
        "## Steps",
        "",
        "| # | Step name | Duration (ms) |",
        "|---|-----------|--------------:|",
    ]
    for i, step in enumerate(steps, 1):
        lines.append(f"| {i} | {step.name} | {step.duration} |")

    # Stats table
    lines += ["", "## Stats", "", "| Metric | Value |", "|--------|-------|"]
    lines += [f"| {k} | {v} |" for k, v in stats]
    lines.append("")
    return "\n".join(lines)


def generate_ab_markdown_report(
    steps_a: Iterable["Step"],
    steps_b: Iterable["Step"],
    stats_a: Sequence[Tuple[str, str]],
    stats_b: Sequence[Tuple[str, str]],
    title: str = "A/B Log Comparison",
    label_a: str = "A",
    label_b: str = "B",
) -> str:
    """
    Generate a Markdown report comparing two runs (A/B).

    Parameters
    ----------
    steps_a : Iterable[Step]
        Steps from run A.
    steps_b : Iterable[Step]
        Steps from run B.
    stats_a : Sequence[Tuple[str, str]]
        Stats for run A.
    stats_b : Sequence[Tuple[str, str]]
        Stats for run B.
    title : str
        The report title.
    label_a : str
        Label for run A.
    label_b : str
        Label for run B.

    Returns
    -------
    str
        Markdown report as a string.
    """
    steps_a = list(steps_a)
    steps_b = list(steps_b)
    steps_dict_a = {s.name: s for s in steps_a}
    steps_dict_b = {s.name: s for s in steps_b}
    all_names = sorted(set(steps_dict_a) | set(steps_dict_b))

    lines: list[str] = [f"# {title}", ""]

    lines += [
        "## Summary\n",
        f"- {label_a}: {len(steps_a)} steps",
        f"- {label_b}: {len(steps_b)} steps",
        "",
    ]

    lines += [
        "## Steps comparison",
        "",
        f"| Step name | {label_a} (ms) | {label_b} (ms) | Δ (ms) |",
        "|-----------|--------------:|--------------:|-------:|",
    ]
    for name in all_names:
        a = steps_dict_a.get(name)
        b = steps_dict_b.get(name)
        dur_a = a.duration if a else None
        dur_b = b.duration if b else None
        delta = None
        if dur_a is not None and dur_b is not None:
            delta = dur_b - dur_a
            sign = "+" if delta >= 0 else ""
            delta_str = f"{sign}{delta}"
        elif dur_a is None:
            delta_str = "new"
        else:
            delta_str = "gone"
        lines.append(
            f"| {name} | "
            f"{dur_a if dur_a is not None else ''} | "
            f"{dur_b if dur_b is not None else ''} | "
            f"{delta_str} |"
        )

    lines += [
        "",
        f"## Stats for {label_a}",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        *[f"| {k} | {v} |" for k, v in stats_a],
        "",
        f"## Stats for {label_b}",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        *[f"| {k} | {v} |" for k, v in stats_b],
        "",
    ]
    return "\n".join(lines)


def make_rich_stats_table(stats: list[tuple[str, str]], title: str) -> Table:
    """
    Create a Rich Table for summary statistics.

    Parameters
    ----------
    stats : list[tuple[str, str]]
        List of (metric, value) tuples to display in the table.
    title : str
        Title for the table (displayed as a heading).

    Returns
    -------
    Table
        Rich Table object ready to print.
    """
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Metric", style="dim", justify="left")
    table.add_column("Value", justify="right")
    for k, v in stats:
        table.add_row(k, v)
    return table


def print_rich_steps_table(steps: Iterable["Step"], title: str = "Slow steps") -> None:
    """
    Print a table of steps using Rich for pretty CLI output.

    Parameters
    ----------
    steps : Iterable[Step]
        List or iterable of Step objects.
    title : str
        Title for the table (default: "Slow steps").
    """
    console = Console()
    table = Table(title=title, show_lines=False, header_style="bold", box=None)
    table.add_column("Step name", style="cyan", no_wrap=True)
    table.add_column("Duration (ms)", style="magenta", justify="right")

    for s in steps:
        table.add_row(s.name, str(s.duration))

    console.print(table)


def print_rich_ab_comparison(
    steps_a: Iterable["Step"],
    steps_b: Iterable["Step"],
    stats_a: list[tuple[str, str]],
    stats_b: list[tuple[str, str]],
    label_a: str = "A",
    label_b: str = "B",
):
    """
    Console A/B comparison using rich.

    Parameters
    ----------
    steps_a : Iterable[Step]
        Steps from run A.
    steps_b : Iterable[Step]
        Steps from run B.
    stats_a : list[tuple[str, str]]
        Statistics for run A.
    stats_b : list[tuple[str, str]]
        Statistics for run B.
    label_a : str
        Label for run A (default: "A").
    label_b : str
        Label for run B (default: "B").
    """
    steps_a = list(steps_a)
    steps_b = list(steps_b)
    steps_dict_a = {s.name: s for s in steps_a}
    steps_dict_b = {s.name: s for s in steps_b}
    all_names = sorted(set(steps_dict_a) | set(steps_dict_b))

    console = Console()
    table = Table(
        title=f"Steps comparison: {label_a} vs {label_b}",
        show_lines=False,
        header_style="bold",
    )
    table.add_column("Step name", style="cyan")
    table.add_column(f"{label_a} (ms)", justify="right", style="magenta")
    table.add_column(f"{label_b} (ms)", justify="right", style="green")
    table.add_column("Δ (ms)", justify="right", style="yellow")

    for name in all_names:
        a = steps_dict_a.get(name)
        b = steps_dict_b.get(name)
        dur_a = a.duration if a else None
        dur_b = b.duration if b else None

        # Calculate delta between runs and set display color
        if dur_a is not None and dur_b is not None:
            delta = dur_b - dur_a
            if delta > 0:
                delta_str = f"[red]+{delta}[/red]"
            elif delta < 0:
                delta_str = f"[green]{delta}[/green]"
            else:
                delta_str = "0"
        elif dur_a is None:
            delta_str = "[bold blue]new[/bold blue]"
        else:
            delta_str = "[dim]gone[/dim]"
        table.add_row(
            name,
            str(dur_a) if dur_a is not None else "",
            str(dur_b) if dur_b is not None else "",
            delta_str,
        )

    # Print steps comparison and stats for each run
    console.print(table)
    a_stats = make_rich_stats_table(stats_a, f"Stats for {label_a}")
    b_stats = make_rich_stats_table(stats_b, f"Stats for {label_b}")
    console.print(Columns([a_stats, b_stats]))
