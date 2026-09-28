from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Callable, TypeVar, overload

from .protocols import Criterion

C = TypeVar("C", bound=type)

class CriterionRegistry:
    def __init__(self) -> None:
        self._criteria: dict[str, Criterion] = {}

    # Overload 1: Decorator usage (no criterion provided)
    @overload
    def register(self, criterion: None = None, *, overwrite: bool = False) -> Callable[[C], C]: ...

    # Overload 2: Programmatic usage (criterion instance provided)
    @overload
    def register(self, criterion: Criterion, *, overwrite: bool = False) -> Criterion: ...
    
    def register(
        self,
        criterion: Criterion | None = None,
        *,
        overwrite: bool = False,
    ) -> Any:
        # 1. Programmatic use: registry.register(MyCriterion())
        if criterion is not None:
            name = criterion.name

            if not name:
                raise ValueError("A criterion must define a non-empty name.")

            if name in self._criteria and not overwrite:
                raise ValueError(
                    f"Criterion {name!r} is already registered."
                )

            self._criteria[name] = criterion
            return criterion

        # 2. Decorator use: @registry.register()
        def wrapper(cls: C) -> C:
            instance = cls()
            self.register(instance, overwrite=overwrite)
            return cls

        return wrapper

    def get(self, name: str) -> Criterion:
        try:
            return self._criteria[name]
        except KeyError as exc:
            available = ", ".join(self.names())
            raise ValueError(
                f"Unknown convergence criterion: {name!r}. "
                f"Available criteria: {available}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._criteria.keys())

    def describe(self, name: str) -> dict[str, Any]:
        criterion = self.get(name)
        params_type = criterion.params_type

        parameters: dict[str, Any] = {}

        if hasattr(params_type, "model_fields"):
            for field_name, field_info in params_type.model_fields.items():
                if field_info.is_required():
                    default = "<required>"
                else:
                    default = field_info.default

                parameters[field_name] = {
                    "type": str(field_info.annotation),
                    "default": default,
                    "description": field_info.description or "",
                }
        elif is_dataclass(params_type):
            for field in fields(params_type):
                if field.default is not MISSING:
                    default = field.default
                elif field.default_factory is not MISSING:
                    default = "<factory>"
                else:
                    default = "<required>"

                parameters[field.name] = {
                    "type": field.type,
                    "default": default,
                    "description": field.metadata.get(
                        "description",
                        "",
                    ),
                }

        return {
            "name": criterion.name,
            "description": criterion.description,
            "assumptions": criterion.assumptions,
            "limitations": criterion.limitations,
            "result_interpretation": criterion.result_interpretation,
            "example_usage": criterion.example_usage,
            "references": criterion.references,
            "parameters": parameters,
            "params_type": params_type,
        }


registry = CriterionRegistry()
