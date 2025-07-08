from __future__ import annotations
from pathlib import Path
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from statistics import mean, median
from typing import Iterable, List, Sequence, Tuple, Dict

from deeptrace.core.models import Step

__all__ = [
    "get_report_path",
    "get_stats",
    "generate_markdown_report",
    "generate_ab_markdown_report",
    "make_rich_stats_table",
    "print_rich_steps_table",
    "print_rich_ab_comparison",
]

# ───────────────────────── helpers ────────────────────────── #

def get_report_path(report_dir: str | Path, fmt: str = "md") -> Path:
    dst = Path(report_dir)
    dst.mkdir(parents=True, exist_ok=True)
    return dst / f"report.{fmt}"

# ───────────────────────── statistics ─────────────────────── #

def _perc(vals: list[int], p: int) -> int:
    if not vals:
        return 0
    if p <= 0:
        return vals[0]
    if p >= 100:
        return vals[-1]
    k = (len(vals) - 1) * p / 100
    f, c = int(k), int(k) + 1
    if c >= len(vals):
        return vals[-1]
    return int(vals[f] * (c - k) + vals[c] * (k - f))

def get_stats(steps: Iterable[Step], percentiles: Sequence[int] = (95, 99)) -> List[Tuple[str, str]]:
    vals = [s.duration for s in steps]
    if not vals:
        return [("Total steps", "0")]
    vals.sort()
    stats: List[Tuple[str, str]] = [
        ("Total steps", str(len(vals))),
        ("Min", f"{vals[0]} ms"),
        ("Max", f"{vals[-1]} ms"),
        ("Median (p50)", f"{int(median(vals))} ms"),
        ("Avg", f"{mean(vals):.1f} ms"),
    ]
    for p in percentiles:
        stats.append((f"P{p}", f"{_perc(vals, p)} ms"))
    return stats

# ───────────────────────── markdown ──────────────────────── #

def generate_markdown_report(steps: Iterable[Step], stats: Sequence[Tuple[str, str]], *,
                              title: str = "DeepTrace Report") -> str:
    steps = list(steps)
    lines = [f"# {title}", ""]
    if not steps:
        lines.append("_No steps found_")
        return "\n".join(lines)

    lines += ["## Steps", "", "| № | Step | ms |", "|---|------|---:|"]
    for i, s in enumerate(steps, 1):
        lines.append(f"| {i} | {s.name} | {s.duration} |")

    lines += ["", "## Stats", "", "| metric | value |", "|--------|-------|"]
    lines += [f"| {k} | {v} |" for k, v in stats]
    return "\n".join(lines)

def generate_ab_markdown_report(steps_a, steps_b, stats_a, stats_b,
                                *, title: str = "A/B Log Comparison",
                                label_a: str = "A", label_b: str = "B") -> str:
    sa, sb = list(steps_a), list(steps_b)
    da, db = {s.name: s for s in sa}, {s.name: s for s in sb}
    names = sorted(set(da) | set(db))

    lines = [f"# {title}", "",
             "## Summary", "",
             f"- {label_a}: {len(sa)} steps",
             f"- {label_b}: {len(sb)} steps", ""]

    lines += ["## Steps comparison", "",
              f"| step | {label_a} | {label_b} | Δ |",
              "|------|------:|------:|----:|"]
    for n in names:
        a = da.get(n)
        b = db.get(n)
        d_a = a.duration if a else ""
        d_b = b.duration if b else ""
        if a and b:
            delta = f"{'+' if b.duration - a.duration >= 0 else ''}{b.duration - a.duration}"
        elif a is None:
            delta = "new"
        else:
            delta = "gone"
        lines.append(f"| {n} | {d_a} | {d_b} | {delta} |")

    def _stats_block(label, stats):
        return ["", f"## Stats for {label}", "",
                "| metric | value |", "|--------|-------|",
                *[f"| {k} | {v} |" for k, v in stats]]
    lines += _stats_block(label_a, stats_a)
    lines += _stats_block(label_b, stats_b)
    return "\n".join(lines)

# ───────────────────────── rich ────────────────────── #

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# Внутренний фабричный метод
# ─────────────────────────────────────────────────────────────────────────────
def _make_table(title: str) -> Table:
    """Единый стиль таблиц: скруглённая рамка + жирные заголовки."""
    return Table(title=title,
                 show_header=True,
                 header_style="bold",
                 box=box.ROUNDED)


# ─────────────────────────────────────────────────────────────────────────────
# Статистика
# ─────────────────────────────────────────────────────────────────────────────
def make_rich_stats_table(stats: List[Tuple[str, str]], title: str) -> Table:
    tbl = _make_table(title)
    tbl.add_column("metric")
    tbl.add_column("value", justify="right")
    for key, val in stats:
        tbl.add_row(key, val)
    return tbl


# ─────────────────────────────────────────────────────────────────────────────
# Краткая сводка
# ─────────────────────────────────────────────────────────────────────────────
def _stats_to_dict(stats: List[Tuple[str, str]]) -> Dict[str, str]:
    return {k: v for k, v in stats}


def print_run_summary(stats: List[Tuple[str, str]], *, title: str = "Run summary") -> None:
    """Печатает небольшую панель-сводку до таблиц."""
    d = _stats_to_dict(stats)
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan")
    grid.add_column(justify="right")
    for key in ("Total steps", "Avg", "Median (p50)", "Min", "Max"):
        if key in d:
            grid.add_row(key.replace(" (p50)", ""), d[key])
    console.print(Panel(grid, title=title, border_style="green"))


# ─────────────────────────────────────────────────────────────────────────────
# Таблица «Slow steps»
# ─────────────────────────────────────────────────────────────────────────────
def print_rich_steps_table(steps: Iterable[Step], *, title: str = "Slow steps") -> None:
    tbl = _make_table(title)
    tbl.add_column("#", justify="right", style="dim")
    tbl.add_column("step")
    tbl.add_column("ms", justify="right")
    for idx, s in enumerate(steps, 1):
        tbl.add_row(str(idx), s.name, str(s.duration))
    console.print(tbl)


# ─────────────────────────────────────────────────────────────────────────────
# A/B сравнение
# ─────────────────────────────────────────────────────────────────────────────
def print_rich_ab_comparison(
    steps_a: Iterable[Step],
    steps_b: Iterable[Step],
    stats_a: List[Tuple[str, str]],
    stats_b: List[Tuple[str, str]],
    *,
    label_a: str = "A",
    label_b: str = "B",
) -> None:
    steps_a, steps_b = list(steps_a), list(steps_b)
    dict_a = {s.name: s for s in steps_a}
    dict_b = {s.name: s for s in steps_b}
    all_names = sorted(dict_a.keys() | dict_b.keys())

    tbl = _make_table(f"Steps comparison: {label_a} vs {label_b}")
    tbl.add_column("step")
    tbl.add_column(label_a, justify="right")
    tbl.add_column(label_b, justify="right")
    tbl.add_column("Δ", justify="right")

    for name in all_names:
        a, b = dict_a.get(name), dict_b.get(name)
        if a and b:
            delta = b.duration - a.duration
            delta_str = f"[red]+{delta}[/]" if delta > 0 else f"[green]{delta}[/]"
        elif a is None:
            delta_str = "[blue]new[/]"
        else:
            delta_str = "[dim]gone[/dim]"
        tbl.add_row(
            name,
            str(a.duration) if a else "",
            str(b.duration) if b else "",
            delta_str,
        )

    console.print(tbl)
    console.print(
        Columns(
            [
                make_rich_stats_table(stats_a, f"Stats {label_a}"),
                make_rich_stats_table(stats_b, f"Stats {label_b}"),
            ]
        )
    )
