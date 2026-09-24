"""Polars namespace registration — ``df.convergence.<criterion>(...)``.

Works only with Polars DataFrames (no LazyFrame in this simplified version).
Auto-discovers ``catable.criterion.*`` files; each ``.py`` must expose
``compute`` and a ``Params`` model. Adding a new file automatically adds a
method ``df.convergence.<name>`` without editing this file.

Pattern mirrors ``df.convergence.clt_absolute(it_col, target_col, ...)`` where
the first two params are always ``it_col`` and ``target_col``.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any

import polars as pl

from catable._schema import validate_frame_has_cols

_CONVERGENCE_METHODS: dict[str, Any] = {}


def _load_criteria() -> dict[str, Any]:
    import catable.criterion as _pkg

    methods: dict[str, Any] = {}
    for mod in pkgutil.iter_modules(_pkg.__path__):
        if mod.name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"catable.criterion.{mod.name}")
        except Exception:
            continue
        if not hasattr(module, "compute"):
            continue
        methods[mod.name] = module
    return methods


_CONVERGENCE_METHODS = _load_criteria()


def _make_namespace_method(name: str, module: Any):  # type: ignore[no-untyped-def]
    """Create a method ``clt_absolute(self, it_col=..., target_col=..., **kw)``."""

    def method(
        self: Any, it_col: str = "it", target_col: str = "value", **kwargs: Any
    ) -> pl.DataFrame:  # type: ignore[no-untyped-def]
        df: pl.DataFrame = self._df
        validate_frame_has_cols(df, it_col=it_col, target_col=target_col)

        # try to instantiate the module's Params model
        params_cls = None
        # clt_absolute uses CltAbsoluteParams
        for cand in [
            "CltAbsoluteParams",
            "Params",
            "CriterionParams",
            f"{name.title().replace('_', '')}Params",
        ]:
            if hasattr(module, cand):
                params_cls = getattr(module, cand)
                break

        # default thresholds for clt_absolute to match spec
        if name == "clt_absolute":
            # ensure defaults: epsilon=0.1, alpha=0.05, threshold=1.0
            kwargs.setdefault("epsilon", 0.1)
            kwargs.setdefault("alpha", 0.05)
            kwargs.setdefault("threshold", 1.0)
            if params_cls is not None:
                params = params_cls(**kwargs)  # type: ignore[operator]
                return module.compute(df, it_col, target_col, params)  # type: ignore[attr-defined]
            return module.compute(df, it_col, target_col, kwargs)  # type: ignore[attr-defined]

        if params_cls is not None:
            params = params_cls(**kwargs)  # type: ignore[operator]
            return module.compute(df, it_col, target_col, params)  # type: ignore[attr-defined]
        return module.compute(df, it_col, target_col, kwargs)  # type: ignore[attr-defined]

    method.__name__ = name
    return method


@pl.api.register_dataframe_namespace("convergence")
class ConvergenceNamespace:
    """Namespace ``df.convergence`` — methods are injected from criterion files."""

    def __init__(self, df: pl.DataFrame) -> None:
        self._df: pl.DataFrame = df


# Inject discovered methods as instance methods on the namespace class
for _name, _mod in _CONVERGENCE_METHODS.items():
    setattr(ConvergenceNamespace, _name, _make_namespace_method(_name, _mod))
