from pathlib import Path

from rich.console import Console

from smal.diagramming.generation import generate_state_machine_svg

console = Console()


def generate_diagram_cmd(smal_path: str | Path, svg_output_dir: str | Path, open: bool = False, force: bool = False, title: bool = True) -> None:
    with console.status(f"Generating state machine diagram for [cyan]{smal_path}[/cyan]", spinner="dots"):
        out_path = generate_state_machine_svg(smal_path, svg_output_dir, open=open, force=force, title=title)
    console.print(f"✅  [green]Diagram generated successfully: {out_path}[/green]")
