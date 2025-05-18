import typer
from pathlib import Path
from .registry import get
from .analyzer import top_slow_steps
from .models import Step

app = typer.Typer()


def _detect_format(path: str) -> str:
    return "playwright"


def _output(steps: list[Step]):
    for i, s in enumerate(steps, 1):
        typer.echo(f"{i}. {s.name} — {s.duration} ms")


@app.command()
def analyze(
    log: Path = typer.Argument(..., help="Log file"),
    top: int = typer.Option(5, help="How many slow steps to show"),
):
    fmt = _detect_format(str(log))
    parser = get(fmt)
    steps = parser.parse(str(log))
    if not steps:
        typer.echo("No steps found", err=True)
        raise typer.Exit(1)
    _output(top_slow_steps(steps, top))


if __name__ == "__main__":
    app()
