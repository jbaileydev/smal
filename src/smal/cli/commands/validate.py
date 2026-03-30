from __future__ import annotations  # Until Python 3.14

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeAlias

from jinja2 import Environment, meta, nodes, TemplateNotFound
from pydantic import BaseModel


@dataclass(frozen=True)
class TemplateRef:
    name: str | None
    line: int
    col: int


@dataclass(frozen=True)
class TemplateVariableRef(TemplateRef):
    name: str
    line: int
    col: int


TemplateMacroRef: TypeAlias = TemplateRef


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SMALValidationIssue:
    severity: Severity
    message: str
    location: tuple[int, int] | None = None
    code: str | None = None


@dataclass
class SMALValidationResult:
    template_name: str
    issues: list[SMALValidationIssue] = field(default_factory=list)

    def add_issue(self, severity: Severity, message: str, location: str | None = None, code: str | None = None) -> None:
        self.issues.append(SMALValidationIssue(severity, message, location, code))

    @property
    def ok(self) -> bool:
        return all(issue.severity != Severity.ERROR for issue in self.issues)


def extract_paths_from_model_schema(model_schema: dict[str, Any], prefix: str = "") -> set[str]:
    """Extracts variable paths from a Pydantic model schema.

    Args:
        model_schema (dict[str, Any]): The JSON schema of the model.
        prefix (str, optional): The prefix for the variable paths. Defaults to "".

    Returns:
        set[str]: A set of variable paths.

    """
    paths = set()
    schema_type = model_schema.get("type")
    if schema_type == "object":
        props = model_schema.get("properties", {})
        for name, subschema in props.items():
            new_prefix = f"{prefix}.{name}" if prefix else name
            paths |= extract_paths_from_model_schema(subschema, new_prefix)
        return paths
    if schema_type == "array":
        items = model_schema.get("items", {})
        new_prefix = f"{prefix}[]" if prefix else "[]"
        return extract_paths_from_model_schema(items, new_prefix)
    if "anyOf" in model_schema:
        for option in model_schema["anyOf"]:
            paths |= extract_paths_from_model_schema(option, prefix)
        return paths
    if "oneOf" in model_schema:
        for option in model_schema["oneOf"]:
            paths |= extract_paths_from_model_schema(option, prefix)
        return paths
    if schema_type in {"string", "number", "integer", "boolean", "null"}:
        paths.add(prefix)
        return paths
    if prefix:
        paths.add(prefix)
    return paths


def extract_template_column(lines: list[str], lineno: int, variable_name: str) -> int:
    if 1 <= lineno <= len(lines):
        text_line = lines[lineno - 1]
        colno = text_line.find(variable_name)
        return colno if colno != -1 else 0
    return 0


def extract_template_variables(env: Environment, template_source: str) -> set[str]:
    """Extracts the set of variable names used in a Jinja2 template.

    Args:
        env (Environment): The Jinja2 environment.
        template_source (str): The source code of the template.

    Returns:
        set[str]: A set of variable names used in the template.

    """
    ast = env.parse(template_source)
    return meta.find_undeclared_variables(ast)


def generate_allowed_variable_paths_from_model(model: type[BaseModel]) -> set[str]:
    """Generates a set of allowed variable paths for a given Pydantic model by analyzing its JSON schema.

    Args:
        model (type[BaseModel]): The Pydantic model class.

    Returns:
        set[str]: A set of allowed variable paths.

    """
    model_schema = model.model_json_schema()
    return extract_paths_from_model_schema(model_schema)


def validate_template_macros(
    env: Environment,
    template_source: str,
    template_name: str,
    result: SMALValidationResult | None = None,
) -> SMALValidationResult:
    ast = env.parse(template_source)
    result = result or SMALValidationResult(template_name)
    for template_macro_ref in walk_template_macros(ast, template_source):
        if not template_macro_ref.name:
            continue
        try:
            env.get_template(template_macro_ref.name)
        except TemplateNotFound:
            result.add_issue(
                Severity.ERROR,
                f"Macro template '{template_macro_ref.name}' not found.",
                f"{template_macro_ref.line}:{template_macro_ref.col}",
                code="MACRO_TEMPLATE_NOT_FOUND",
            )
    return result


def validate_template_variables(
    env: Environment,
    template_source: str,
    template_name: str,
    allowed_paths: set[str],
    result: SMALValidationResult | None = None,
) -> SMALValidationResult:
    used_template_variables = extract_template_variables(env, template_source)
    result = result or SMALValidationResult(template_name)

    def is_allowed_symbol(symbol: str) -> bool:
        if symbol in allowed_paths:
            return True
        prefix_dot = symbol + "."
        prefix_arr = symbol + "[]"
        for p in allowed_paths:
            if p.startswith(prefix_dot) or p.startswith(prefix_arr):
                return True
        return False

    for var in sorted(used_template_variables):
        # Skip special Jinja2 variables
        if var in {"loop"}:
            continue
        if not is_allowed_symbol(var):
            result.add_issue(
                Severity.ERROR,
                f"Unknown variable '{var}' used in template '{template_name}'",
                location=f"template variable '{var}'",
                code="undefined_variable",
            )
    return result


def walk_template_macros(ast: nodes.Template, template_source: str) -> Iterator[TemplateMacroRef]:
    lines = template_source.splitlines()
    for node in ast.find_all(nodes.FromImport):
        template_ref = node.template.value if isinstance(node.template, nodes.Const) else None
        macro_colno = extract_template_column(lines, node.lineno, "import")
        yield TemplateMacroRef(template_ref, node.lineno, macro_colno)


def walk_template_variables(ast: nodes.Template, template_source: str) -> Iterator[TemplateVariableRef]:
    lines = template_source.splitlines()
    for node in ast.find_all(nodes.Name):
        variable_name = node.name
        variable_lineno = node.lineno
        variable_colno = extract_template_column(lines, variable_lineno, variable_name)
        yield TemplateVariableRef(variable_name, variable_lineno, variable_colno)
