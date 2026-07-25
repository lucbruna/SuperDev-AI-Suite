import typer
from cli.commands.init import init
from cli.commands.doctor import doctor

app = typer.Typer(name="superdev")

app.command(name="init")(init)
app.command(name="doctor")(doctor)

def cli():
    app()