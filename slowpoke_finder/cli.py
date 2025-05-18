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
    top: int = typer.Option(5, "--top", "-n", help="Показать топ N медленных шагов"),
    threshold: int = typer.Option(
        None, "--threshold", "-t", help="Пороговое значение длительности шага (ms)"
    ),
):
    try:
        parser = get(format)
    except ValueError:
        typer.echo(f"Неизвестный формат: {format}", err=True)
        raise typer.Exit(2)

    try:
        steps = list(parser.parse(log))
    except Exception as e:
        typer.echo(f"Ошибка разбора лога: {e}", err=True)
        raise typer.Exit(3)

    if not steps:
        typer.echo("Шаги не найдены", err=True)
        raise typer.Exit(1)

    if threshold is not None:
        filtered = [step for step in steps if step.duration >= threshold]
        if not filtered:
            typer.echo(f"Нет шагов с длительностью >= {threshold} ms")
            raise typer.Exit(0)
        for i, step in enumerate(filtered, 1):
            typer.echo(f"{i}. {step.name} - {step.duration} ms")
    else:
        top_steps = top_slow_steps(steps, top)
        for i, step in enumerate(top_steps, 1):
            typer.echo(f"{i}. {step.name} - {step.duration} ms")
