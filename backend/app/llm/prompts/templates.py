"""Prompt template library with versioning."""

import re
from pathlib import Path
from string import Template
from typing import Any

from app.core.logging import get_logger


class PromptTemplate:
    """A single prompt template with safe variable substitution."""

    def __init__(self, template_string: str, name: str = "anonymous") -> None:
        self.name = name
        self.template = Template(template_string)
        self.raw = template_string

    def render(self, **kwargs: Any) -> str:
        """Render template with variables."""
        return self.template.safe_substitute(**kwargs)

    def required_variables(self) -> set[str]:
        """Return variables referenced by this template."""
        pattern = re.compile(r"\$\{?(\w+)\}?")
        return set(pattern.findall(self.raw))


class PromptLibrary:
    """Collection of named prompt templates loaded from .txt files."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._templates: dict[str, PromptTemplate] = {}

    def load_from_directory(self, path: Path) -> None:
        """Load all .txt files in a directory."""
        if not path.exists():
            raise ValueError(f"Template directory does not exist: {path}")

        for txt_file in path.glob("*.txt"):
            name = txt_file.stem
            content = txt_file.read_text(encoding="utf-8")
            self._templates[name] = PromptTemplate(content, name=name)
            self.logger.debug("loaded_template", name=name)

    def get(self, name: str) -> PromptTemplate:
        """Get a template by name."""
        if name not in self._templates:
            raise KeyError(f"Template not found: {name}")
        return self._templates[name]

    def list_templates(self) -> list[str]:
        """List loaded template names."""
        return sorted(self._templates.keys())
