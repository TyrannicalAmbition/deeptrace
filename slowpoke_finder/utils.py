from __future__ import annotations

from pathlib import Path
from tabulate import tabulate  # type: ignore
from typing import List, Tuple

__all__ = [
    "get_report_path",
    "get_stats",
    "generate_markdown_report",
    "print_steps_table",
    "print_stats",
]


# ---------- FS helpers ----------


def get_report_path(report_dir: str | Path, fmt: str = "md") -> Path:
    """Return path like <report_dir>/report.<fmt> and create directory if needed."""
    dir_path = Path(report_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path / f"report.{fmt}"


# ---------- Stats ----------


def get_stats(steps) -> List[Tuple[str, str]]:
    durations = [s.duration for s in steps]
    if not durations:
        return [
            ("Total steps", "0"),
            ("Min", "0 ms"),
            ("Max", "0 ms"),
            ("Median", "0 ms"),
            ("Avg", "0 ms"),
        ]
    total = len(durations)
    durations.sort()
    minv, maxv = durations[0], durations[-1]
    median = (
        durations[total // 2]
        if total % 2
        else sum(durations[total // 2 - 1 : total // 2 + 1]) / 2
    )
    avg = sum(durations) / total
    return [
        ("Total steps", str(steps)),
        ("Min", f"{minv} ms"),
        ("Max", f"{maxv} ms"),
        ("Median", f"{int(median)} ms"),
        ("Avg", f"{avg:.1f} ms"),
    ]


# ---------- Rendering ----------


def generate_markdown_report(
    steps, stats, title: str = "Slowpoke Finder Report"
) -> str:
    lines: list[str] = [f"# {title}", ""]
    if not steps:
        return "\n".join(lines + ["_No steps found._"])

    lines += [
        "## Steps",
        "",
        "| # | Step name | Duration (ms) |",
        "|---|-----------|--------------:|",
    ]
    for i, step in enumerate(steps, 1):
        lines.append(f"| {i} | {step.name} | {step.duration} |")
    lines += ["", "## Stats", "", "| Metric | Value |", "|--------|-------|"]
    lines += [f"| {k} | {v} |" for k, v in stats]
    lines.append("")
    return "\n".join(lines)


def print_steps_table(steps, title: str = "Top slowest steps") -> None:
    from typer import echo

    echo()
    echo(f"## {title}")
    if not steps:
        echo("_No steps to display_")
        return
    echo(
        tabulate(
            [(s.name, s.duration) for s in steps],
            headers=["Step name", "Duration (ms)"],
            tablefmt="github",
        )
    )


def print_stats(stats) -> None:
    from typer import echo

    echo()
    echo("**Stats**")
    echo(tabulate(stats, tablefmt="github"))
