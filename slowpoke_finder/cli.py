import typer
from pathlib import Path
from slowpoke_finder.registry import get

app = typer.Typer()


@app.command()
def analyze(
    log: str = typer.Argument(..., help="Path to log file or log folder"),
    format: str = typer.Option(
        ..., "--format", "-f", help="Log format: playwright, selenium, allure"
    ),
    top: int = typer.Option(5, "--top", "-n", help="Show top N slow steps"),
    threshold: int = typer.Option(
        None, "--threshold", "-t", help="Step duration threshold (ms)"
    ),
):
    log_path = Path(log)
    paths = []
    if log_path.is_dir():
        paths = list(log_path.rglob("*.json")) + list(log_path.rglob("*.har"))
        if not paths:
            typer.echo(f"No matching files found in {log} folder", err=True)
            raise typer.Exit(1)
    else:
        paths = [log_path]

    all_steps = []
    try:
        parser = get(format)
    except ValueError:
        typer.echo(f"Unknown format: {format}", err=True)
        raise typer.Exit(2)

    for file_path in paths:
        try:
            steps = list(parser.parse(str(file_path)))
            all_steps.extend(steps)
        except Exception as e:
            typer.echo(f"Error parsing file {file_path}: {e}", err=True)

    if not all_steps:
        typer.echo("No steps found", err=True)
        raise typer.Exit(1)

    if threshold is not None:
        filtered = [step for step in all_steps if step.duration >= threshold]
        if not filtered:
            typer.echo(f"No steps with duration >= {threshold} ms")
            raise typer.Exit(0)
        for i, step in enumerate(filtered, 1):
            typer.echo(f"{i}. {step.name} - {step.duration} ms")
    else:
        from slowpoke_finder.analyzer import top_slow_steps

        top_steps = top_slow_steps(all_steps, top)
        for i, step in enumerate(top_steps, 1):
            typer.echo(f"{i}. {step.name} - {step.duration} ms")
