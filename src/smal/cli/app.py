from pathlib import Path

import typer

from smal.cli.commands import generate_diagram_cmd, install_graphviz_app

app = typer.Typer(help="SMAL = State Machine Abstraction Language CLI")
app.add_typer(install_graphviz_app, name="install-graphviz")


@app.command(name="diagram", help="Generate an SVG state machine diagram from a SMAL file.")
def diagram_cmd(
    smal_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="Path to the input .smal YAML file."),
    svg_output_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, writable=True, help="Directory where the generated SVG diagram will be written."),
    open: bool = typer.Option(False, "--open", "-o", help="Open the generated SVG after creation."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing SVG files if they already exist."),
    title: bool = typer.Option(True, "--title", "-t", help="Include the state machine title in the diagram."),
) -> None:
    generate_diagram_cmd(
        smal_path=smal_path,
        svg_output_dir=svg_output_dir,
        open=open,
        force=force,
        title=title,
    )
