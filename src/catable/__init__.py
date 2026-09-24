"""catable — convergence analysis that works with Polars."""

from __future__ import annotations

# Register Polars namespace on import (df.convergence.*)
from catable import _namespace as _  # noqa: F401

__all__ = ["__version__"]

__version__ = "0.1.0"
