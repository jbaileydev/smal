import os
from pathlib import Path

import typer

from smal.cli.commands import generate_code_cmd_builtin, generate_diagram_cmd, install_graphviz_app
from smal.cli.commands.code import generate_code_cmd_custom
from smal.cli.commands.helpers import echo_table
from smal.cli.commands.validate import generate_allowed_variable_paths_from_model, validate_template_macros, validate_template_variables
from smal.codegen.code_generator import SMALCodeGenerator
from smal.codegen.smal_templates import TemplateRegistry, is_valid_smal_template
from smal.schemas.smal_file import SMALFile

app = typer.Typer(help="SMAL = State Machine Abstraction Language CLI")
app.add_typer(install_graphviz_app, name="install-graphviz")


@app.command(name="templates", help="Get a manifest of all provided code generation templates SMAL provides.")
def templates_cmd() -> None:
    echo_table("SMAL Builtin Codegen Templates", ["Name", "Lang", "Description"], [[tmpl.name, tmpl.lang, tmpl.description] for tmpl in TemplateRegistry.list_templates()])


@app.command(name="code", help="Generate code from a SMAL file using a standard or custom Jinja2 template.")
def code_cmd(
    smal_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="Path to the input SMAL file."),
    template: str = typer.Option(
        None, "--template", "-t", help="Name of the builtin SMAL template to generate, or the filepath to a custom, SMAL-compliant Jinja2 template to generate."
    ),
    out_dir: Path = typer.Option(
        Path("./generated"), "--out", "-o", file_okay=False, dir_okay=True, writable=True, help="Directory where generated code will be written (default: ./generated)."
    ),
    out_filename: str = typer.Option(
        None, "--filename", "-n", help="Optional filename for the generated code. If not provided, a default name based on the template will be used."
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files if they already exist."),
) -> None:
    # Validate output directory existence and writability
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
    elif not out_dir.is_dir():
        raise typer.BadParameter(f"Output path exists but is not a directory: {out_dir}")
    # If the user selected a builtin template
    if TemplateRegistry.has_template(template):
        # Generate the code using the built-in template
        generate_code_cmd_builtin(
            smal_path=smal_path,
            template_name=template,
            out_dir=out_dir,
            out_filename=out_filename,
            force=force,
        )
    # If the user selected a custom template
    else:
        custom_template_path = Path(template)
        # Validate that the custom template file exists and is readable
        if not custom_template_path.is_file():
            raise typer.BadParameter(f"Custom template file not found: {custom_template_path}")
        if not os.access(custom_template_path, os.R_OK):
            raise typer.BadParameter(f"Custom template file is not readable: {custom_template_path}")
        # Validate that the custom template itself is a valid SMAL template by checking for required variables
        is_valid_tmpl, invalid_vars = is_valid_smal_template(custom_template_path)
        if not is_valid_tmpl:
            raise typer.BadParameter(f"Custom template {custom_template_path} is not a valid SMAL template. Invalid variables referenced: {', '.join(invalid_vars)}.")
        # Generate the custom code
        generate_code_cmd_custom(
            smal_path=smal_path,
            custom_template_path=custom_template_path,
            out_dir=out_dir,
            out_filename=out_filename,
            force=force,
        )


@app.command(name="diagram", help="Generate an SVG state machine diagram from a SMAL file.")
def diagram_cmd(
    smal_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="Path to the input SMAL file."),
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


@app.command(name="validate", help="Validate a custom Jinja2 template for use with SMAL code generation by checking for undefined variables and missing macro templates.")
def validate_cmd(
    template_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True, help="Path to the Jinja2 template file."),
) -> None:
    generator = SMALCodeGenerator()
    env, template = generator.load_external_template(template_path)
    allowed_variable_paths = generate_allowed_variable_paths_from_model(SMALFile)
    if env.loader is None or template.name is None:
        raise RuntimeError("Jinja2 Environment loader is not configured.")
    source, _, _ = env.loader.get_source(env, template.name)
    validation_result = validate_template_variables(env, source, template.name, allowed_variable_paths)
    validation_result = validate_template_macros(env, source, template.name, result=validation_result)
    if validation_result.ok:
        typer.echo(f"Template '{template_path}' is valid! No issues found.")
    else:
        typer.echo(f"Template '{template_path}' has {len(validation_result.issues)} issue(s):")
        for issue in validation_result.issues:
            typer.echo(f"- [{issue.severity.value.upper()}] {issue.message} (Location: {issue.location}, Code: {issue.code})")


if __name__ == "__main__":
    app()
