"""Public convergence API — ty-friendly import path.

Preferred import for type checkers::

    from catable.convergence import clt_absolute

Each criterion is implemented in ``catable.criterion.<name>.py`` with a
predefined structure (``Params`` + ``compute``). This module auto-discovers
those files so adding a new ``criterion/foo.py`` automatically exposes
``from catable.convergence import foo`` and ``df.convergence.foo``.

For Polars ergonomics the same functions are also exposed via the
``df.convergence.<criterion>`` namespace registered in ``_namespace.py``.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import Any

import polars as pl  # noqa: TC002

from catable._schema import validate_frame_has_cols

# ---------------------------------------------------------------------------
# Explicit wrapper for clt_absolute — keeps signature discoverable by ty
# ---------------------------------------------------------------------------


def clt_absolute(
    df: pl.DataFrame,
    it_col: str = "it",
    target_col: str = "value",
    epsilon: float = 0.1,
    alpha: float = 0.05,
    threshold: float = 1.0,
) -> pl.DataFrame:
    """CLT absolute convergence — returns table ``it | criterion | converged``.

    Args:
        df: Polars DataFrame with columns ``it_col`` and ``target_col``.
        it_col: iteration column (first param).
        target_col: value column to analyse (second param).
        epsilon: legacy alias for ``threshold``; kept for compatibility.
        alpha: significance level for CLT interval (default 0.05 → z≈1.96).
        threshold: absolute half-width must be ``<= threshold`` to be
            considered converged. For the 50-iteration triangular example
            use ``threshold=1``.

    Returns:
        Polars DataFrame with columns ``it``, ``criterion``, ``converged``.
    """
    validate_frame_has_cols(df, it_col=it_col, target_col=target_col)

    # lazy import to avoid circular import with _namespace
    from catable.criterion.clt_absolute import CltAbsoluteParams, compute

    params = CltAbsoluteParams(epsilon=epsilon, alpha=alpha, threshold=threshold)
    return compute(df, it_col=it_col, target_col=target_col, params=params)


# ---------------------------------------------------------------------------
# Auto-discovery for future criteria — injects <name> into this module's
# globals so ``from catable.convergence import <name>`` works without
# editing this file. Keeps collaboration simple: just add a .py file.
# ---------------------------------------------------------------------------


def _discover_and_register() -> None:
    import catable.criterion as _pkg

    for mod in pkgutil.iter_modules(_pkg.__path__):
        name = mod.name
        if name.startswith("_") or name == "clt_absolute":
            # clt_absolute already explicitly defined above with a typed signature
            continue
        try:
            module = importlib.import_module(f"catable.criterion.{name}")
        except Exception:
            continue
        if not hasattr(module, "compute"):
            continue

        # create a generic wrapper that validates frame and forwards to module.compute
        def _make_wrapper(_module: Any, _name: str):  # type: ignore[no-untyped-def]
            def wrapper(
                df: pl.DataFrame,
                it_col: str = "it",
                target_col: str = "value",
                **kwargs: Any,
            ) -> pl.DataFrame:
                validate_frame_has_cols(df, it_col=it_col, target_col=target_col)
                # try to find a Params model: <Name>Params or Params
                params_cls = None
                for cand in [
                    f"{_name.title().replace('_', '')}Params",
                    "Params",
                    "CriterionParams",
                ]:
                    if hasattr(_module, cand):
                        params_cls = getattr(_module, cand)
                        break
                if params_cls is not None:
                    params = params_cls(**kwargs)  # type: ignore[operator]
                    return _module.compute(df, it_col, target_col, params)  # type: ignore[attr-defined]
                return _module.compute(df, it_col, target_col, kwargs)  # type: ignore[attr-defined]

            wrapper.__name__ = _name
            wrapper.__qualname__ = _name
            return wrapper

        globals()[name] = _make_wrapper(module, name)


_discover_and_register()
