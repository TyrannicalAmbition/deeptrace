"""
Generate a fully-self-contained HTML A/B performance report.

The report contains:
* horizontal bar chart (Top-10 the slowest steps);
* sortable comparison table;
* no external servers – works via `slowpoke-finder view-report`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape  # type: ignore

from slowpoke_finder.models import Step

# --------------------------------------------------------------------------- #
# Jinja environment
# --------------------------------------------------------------------------- #

env = Environment(
    loader=PackageLoader(__package__, "templates"), autoescape=select_autoescape()
)

_ASSETS = ("plotly.min.js", "style.css")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _build_rows(steps_a: List[Step], steps_b: List[Step]) -> list[dict]:
    """
    Merge two step-lists into a diff table.

    Both lists are assumed to be *deduplicated averages*.
    Matching is done by exact step ``name``.
    """
    map_a = {s.name: s.duration for s in steps_a}
    map_b = {s.name: s.duration for s in steps_b}
    all_names = sorted(set(map_a) | set(map_b))

    rows: list[dict] = []
    for name in all_names:
        a = map_a.get(name)
        b = map_b.get(name)
        diff = b - a if a is not None and b is not None else None
        diff_pct = round((b - a) / a * 100, 1) if a and b else None
        rows.append(dict(name=name, a=a, b=b, diff=diff, diff_pct=diff_pct))
    return rows


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def build_ab_report_html(
    steps_a: List[Step],
    steps_b: List[Step],
    name_a: str,
    name_b: str,
    out_dir: Path | str = "ab-report",
) -> Path:
    """
    Create an interactive HTML report comparing two test runs.

    Parameters
    ----------
    steps_a, steps_b
        Deduplicated step lists for run *A* and *B*.
    name_a, name_b
        Labels used in the chart legend.
    out_dir
        Target directory; will be created if missing.

    Returns
    -------
    Path
        Absolute path to the generated ``index.html``.
    """
    out_path = Path(out_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ diff
    rows = _build_rows(steps_a, steps_b)

    # store raw JSON (handy for debug)
    (out_path / "ab_data.json").write_text(json.dumps(rows, indent=2), "utf-8")

    # ---------------------------------------------------------------- render
    html = env.get_template("index.html.j2").render(
        name_a=name_a,
        name_b=name_b,
    )
    (out_path / "index.html").write_text(html, "utf-8")

    # -------------------------------------------------------------- copy assets
    try:
        from importlib.resources import files  # python ≥3.9
    except ImportError:  # pragma: no cover  (fallback for 3.8)
        from importlib_resources import files  # type: ignore

    assets_src = files("slowpoke_finder.ab_reporting.assets")
    assets_dst = out_path / "assets"
    assets_dst.mkdir(exist_ok=True)
    for file_name in _ASSETS:
        (assets_dst / file_name).write_bytes((assets_src / file_name).read_bytes())

    return out_path / "index.html"
