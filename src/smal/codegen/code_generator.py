"""Module defining the code generator for the SMAL CLI program."""

from __future__ import annotations  # Until Python 3.14

from pathlib import Path
from typing import Any

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, StrictUndefined, Template, meta, select_autoescape

from smal.codegen.templates.builtin_templates import SMALTemplate, TemplateRegistry
from smal.schemas.state_machine import SMALFile  # noqa: TC001


class SMALCodeGenerator:
    """Code generator that takes in a SMAL file and generates jinja templated code."""

    def __init__(self) -> None:
        """Initialize the SMALCodeGenerator."""
        self._internal_loader = PackageLoader("smal", "codegen/templates")

    def _build_env(self, external_template_dir: str | Path | None = None) -> Environment:
        if external_template_dir:
            return Environment(
                loader=ChoiceLoader([self._internal_loader, FileSystemLoader(external_template_dir)]),
                autoescape=select_autoescape([]),
                trim_blocks=True,
                lstrip_blocks=True,
                undefined=StrictUndefined,
            )
        return Environment(
            loader=self._internal_loader,
            autoescape=select_autoescape([]),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=StrictUndefined,
        )

    def _detect_unprovided_vars(self, env: Environment, template_name: str, smal: SMALFile, **extra_context: Any) -> set[str]:
        context = {"smal": smal, **extra_context}
        provided_vars = set(context.keys())
        expected_vars = self.get_template_variables(env, template_name)
        missing_vars = expected_vars - provided_vars
        return missing_vars

    @staticmethod
    def get_template_variables(env: Environment, template_name: str) -> set[str]:
        """Get the variables that a jinja template expects.

        Args:
            env (Environment): The environment for the template.
            template_name (str): The name of the template.

        Returns:
            set[str]: The variables that the given jinja template expects.

        """
        source = env.loader.get_source(env, template_name)[0]
        ast = env.parse(source)
        return meta.find_undeclared_variables(ast)

    def load_builtin_template(self, template_name: str) -> tuple[Environment, Template, SMALTemplate]:
        """Load a SMAL-provided built in jinja template.

        Args:
            template_name (str): The name of the builtin template to load.

        Returns:
            tuple[Environment, Template, SMALTemplate]: The jinja environment, jinja template and SMALTemplate objects.

        """
        env = self._build_env()
        smal_tmpl = TemplateRegistry.get(template_name)
        tmpl = env.get_template(smal_tmpl.filename)
        return env, tmpl, smal_tmpl

    def load_external_template(self, external_template_filepath: str | Path) -> tuple[Environment, Template]:
        """Load a jinja template that is externally provided by the user.

        Args:
            external_template_filepath (str | Path): The filepath to the user-provided template.

        Raises:
            FileNotFoundError: If the file could not be found.

        Returns:
            tuple[Environment, Template]: The jinja environment and template.

        """
        external_template_filepath = Path(external_template_filepath)
        if not external_template_filepath.is_file():
            raise FileNotFoundError(f"Template file does not exist: {external_template_filepath}")
        env = self._build_env(external_template_dir=external_template_filepath.parent)
        tmpl = env.get_template(external_template_filepath.name)
        return env, tmpl

    def render(self, template: Template, smal: SMALFile, **extra_context: Any) -> str:
        """Render the given template using the given SMAL file, and any provided extra content.

        Args:
            template (Template): The jinja template to render.
            smal (SMALFile): The SMAL file to render to the template.
            **extra_context (Any): Any extra content provided as kwargs to render in the template.

        Returns:
            str: The rendered template, ready to be written to a file.

        """
        # First, ensure that this template can be rendered
        missing_vars = self._detect_unprovided_vars(template.environment, template.name, smal, **extra_context)
        if missing_vars:
            raise ValueError(
                f"Unable to render template. The following variables are missing from the context: {', '.join(missing_vars)}."
                " Consider adding definitions of these variables in the metadata of your SMAL file.",
            )
        # TODO: Implement formatting while the text is in memory here
        return template.render(smal=smal, **extra_context)

    def render_to_file(self, template: Template, smal: SMALFile, out_path: str | Path, force: bool = False, **extra_context: Any) -> None:
        """Render the given template using the given SMAL file, and any provided extra content to the given filepath.

        Args:
            template (Template): The jinja template to render.
            smal (SMALFile): The SMAL file to render to the template.
            out_path (str | Path): The output filepath to write the file content to.
            force (bool, optional): Whether or not to forcefully overwrite an existing file. Defaults to False.
            **extra_context (Any): Any extra content provided as kwargs to render in the template.

        Raises:
            FileExistsError: If the file already exists and force is false.

        """
        out_path = Path(out_path)
        if not force and out_path.exists():
            raise FileExistsError(f"File already exists and overwrite is not allowed: {out_path}")
        code = self.render(template, smal, **extra_context)
        out_path.write_text(code, encoding="utf-8")
