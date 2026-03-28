import typer

from smal.cli.commands.install_graphviz import install_graphviz_app

app = typer.Typer(help="SMAL = State Machine Abstraction Language CLI")
app.add_typer(install_graphviz_app, name="install-graphviz")
