from deeptrace.commands import analyze, compare
import typer

app = typer.Typer()

app.command(name="analyze")(analyze.analyze)
app.command(name="compare")(compare.compare)

if __name__ == "__main__":
    app()
