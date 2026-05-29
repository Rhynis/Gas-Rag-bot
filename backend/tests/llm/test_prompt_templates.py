"""Tests for prompt templates and prompt library loading."""

from pathlib import Path

import pytest

from app.llm.prompts.templates import PromptLibrary, PromptTemplate


def test_render_with_all_variables() -> None:
    template = PromptTemplate("Xin chào ${name}, đơn hàng $order đã sẵn sàng")

    assert template.render(name="An", order="A001") == "Xin chào An, đơn hàng A001 đã sẵn sàng"


def test_render_with_missing_variable_keeps_placeholder() -> None:
    template = PromptTemplate("Xin chào ${name}, đơn hàng ${order}")

    assert template.render(name="An") == "Xin chào An, đơn hàng ${order}"


def test_required_variables_returns_correct_set() -> None:
    template = PromptTemplate("${context}\n$query\n$conversation_history")

    assert template.required_variables() == {"context", "query", "conversation_history"}


def test_library_loads_all_templates_from_directory(tmp_path: Path) -> None:
    (tmp_path / "first.txt").write_text("Xin chào ${name}", encoding="utf-8")
    (tmp_path / "second.txt").write_text("Đặt hàng ${product}", encoding="utf-8")
    library = PromptLibrary()

    library.load_from_directory(tmp_path)

    assert library.list_templates() == ["first", "second"]
    assert library.get("first").render(name="An") == "Xin chào An"


def test_library_get_unknown_template_raises(tmp_path: Path) -> None:
    library = PromptLibrary()
    library.load_from_directory(tmp_path)

    with pytest.raises(KeyError):
        library.get("missing")
