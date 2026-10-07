"""Tests for CriterionRegistry."""
# uv run pytest tests/test_registry.py

from collections.abc import Sequence
from typing import Any, ClassVar

import pytest
from pydantic import BaseModel

from mocaco.registry import CriterionRegistry, registry


def test_register_decorator() -> None:
    """@registry.register() adds criterion."""

    @registry.register()
    class TestCriterion:
        name = "test_criterion"
        supports_eval_frequency = False
        description = "Test"
        params_type = object
        assumptions: ClassVar[Sequence[str]] = ()
        limitations: ClassVar[Sequence[str]] = ()
        result_interpretation = ""
        example_usage = ""
        references: ClassVar[Sequence[str]] = ()

        def run(self, samples: Any, params: Any) -> Any:
            pass

    assert "test_criterion" in registry.names()


def test_register_programmatic() -> None:
    """registry.register(instance) adds criterion."""
    reg = CriterionRegistry()

    class ProgCriterion:
        name = "prog_test"
        supports_eval_frequency = False
        description = "Test"
        params_type = object
        assumptions: ClassVar[Sequence[str]] = ()
        limitations: ClassVar[Sequence[str]] = ()
        result_interpretation = ""
        example_usage = ""
        references: ClassVar[Sequence[str]] = ()

        def run(self, samples: Any, params: Any) -> Any:
            pass

    criterion = ProgCriterion()
    reg.register(criterion)  # type: ignore[arg-type]
    assert "prog_test" in reg.names()


def test_register_duplicate_raises() -> None:
    """ValueError on duplicate name."""

    @registry.register()
    class FirstCriterion:
        name = "dup_test"
        supports_eval_frequency = False
        description = "First"
        params_type = object
        assumptions: ClassVar[Sequence[str]] = ()
        limitations: ClassVar[Sequence[str]] = ()
        result_interpretation = ""
        example_usage = ""
        references: ClassVar[Sequence[str]] = ()

        def run(self, samples: Any, params: Any) -> Any:
            pass

    with pytest.raises(ValueError, match=r"already registered"):

        @registry.register()
        class SecondCriterion:
            name = "dup_test"
            supports_eval_frequency = False
            description = "Second"
            params_type = object
            assumptions: ClassVar[Sequence[str]] = ()
            limitations: ClassVar[Sequence[str]] = ()
            result_interpretation = ""
            example_usage = ""
            references: ClassVar[Sequence[str]] = ()

            def run(self, samples: Any, params: Any) -> Any:
                pass


class DummyParams(BaseModel):
    threshold: float = 0.5


def test_register_overwrite_allows_duplicate() -> None:
    """overwrite=True replaces existing."""

    @registry.register(overwrite=True)
    class OverwriteCriterion:
        name = "clt_absolute"
        supports_eval_frequency = True
        description = "Overwritten"

        params_type = DummyParams

        assumptions: ClassVar[Sequence[str]] = ()
        limitations: ClassVar[Sequence[str]] = ()
        result_interpretation = ""
        example_usage = ""
        references: ClassVar[Sequence[str]] = ()

        def run(self, samples: Any, params: Any) -> Any:
            pass

    assert registry.names().count("clt_absolute") == 1


def test_register_empty_name_raises() -> None:
    """ValueError when criterion.name is empty."""
    reg = CriterionRegistry()

    with pytest.raises(ValueError, match=r"A criterion must define a non-empty name."):

        @reg.register()
        class EmptyNameCriterion:
            name = ""
            supports_eval_frequency = False
            description = "Test"
            params_type = object
            assumptions = ()
            limitations = ()
            result_interpretation = ""
            example_usage = ""
            references = ()

            def run(self, samples, params):
                pass


def test_get_existing() -> None:
    """Returns correct criterion instance."""
    criterion = registry.get("clt_absolute")
    assert criterion.name == "clt_absolute"


def test_get_unknown_raises() -> None:
    """ValueError with available names in message."""
    with pytest.raises(ValueError, match=r"Unknown convergence criterion: 'nonexistent'"):
        registry.get("nonexistent")


def test_names_returns_tuple() -> None:
    """Returns tuple of registered names."""
    names = registry.names()
    assert isinstance(names, tuple)


def test_names_empty_initially() -> None:
    """Empty tuple for fresh registry."""
    reg = CriterionRegistry()
    assert reg.names() == ()


def test_describe_existing(capsys) -> None:
    """describe() prints panel and table (capsys)."""
    registry.describe("clt_absolute")
    captured = capsys.readouterr()
    assert captured.out != ""


def test_describe_unknown_prints_error(capsys: pytest.CaptureFixture[str]) -> None:
    """describe() prints error for unknown name."""
    registry.describe("nonexistent_method")
    captured = capsys.readouterr()
    assert "Error:" in captured.out
    assert "not found in registry" in captured.out


def test_registry_is_singleton() -> None:
    """Module-level registry is shared."""
    from mocaco.registry import registry as reg2

    assert registry is reg2
