from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import Any

from .protocols import Criterion


class CriterionRegistry:
    def __init__(self) -> None:
        self._criteria: dict[str, Criterion] = {}

    def register(
        self,
        criterion: Criterion,
        *,
        overwrite: bool = False,
    ) -> None:
        name = criterion.name

        if not name:
            raise ValueError("A criterion must define a non-empty name.")

        if name in self._criteria and not overwrite:
            raise ValueError(
                f"Criterion {name!r} is already registered."
            )

        self._criteria[name] = criterion

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

        if is_dataclass(params_type):
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
            "parameters": parameters,
            "params_type": params_type,
        }


registry = CriterionRegistry()
