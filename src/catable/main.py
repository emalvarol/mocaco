"""Main entry — keeps requested ``main.py`` structure.

The actual logic lives in ``catable.convergence`` and
``catable.criterion.*``. This file re-exports for the requested
``main.py + criterion/`` layout while the package is installed as
``src/catable``.

Use::

    from catable.convergence import clt_absolute
    # or
    df.convergence.clt_absolute(it_col="it", target_col="value")

"""

from __future__ import annotations

from catable.convergence import clt_absolute

__all__ = ["clt_absolute"]
