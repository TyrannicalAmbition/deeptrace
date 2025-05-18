import typer
from slowpoke_finder.registry import get
from slowpoke_finder.analyzer import top_slow_steps

app = typer.Typer()


@app.command()
def analyze(
    log: str = typer.Argument(..., help="Путь к файлу лога"),
    format: str = typer.Option(
        ..., "--format", "-f", help="Формат лога: playwright или selenium"
    ),
    top: int = typer.Option(5, help="Показать топ N медленных шагов"),
):
    try:
        parser = get(format)
    except ValueError:
        typer.echo(f"Неизвестный формат: {format}", err=True)
        raise typer.Exit(2)

    try:
        steps = parser.parse(log)
    except Exception as e:
        typer.echo(f"Ошибка разбора лога: {e}", err=True)
        raise typer.Exit(3)

    if not steps:
        typer.echo("Шаги не найдены", err=True)
        raise typer.Exit(1)

    top_steps = top_slow_steps(steps, top)
    for i, step in enumerate(top_steps, 1):
        typer.echo(f"{i}. {step.name} - {step.duration} ms")
