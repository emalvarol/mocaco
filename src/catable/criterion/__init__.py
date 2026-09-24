"""Criterion package.

Each ``*.py`` file inside this package must expose a ``compute`` function
and a ``Params`` model (predefined structure). See ``clt_absolute.py`` for
the template. Auto-discovery is performed by ``catable.convergence`` and
``catable._namespace`` so adding a new file automatically exposes
``df.convergence.<name>`` and ``from catable.convergence import <name>``.
"""
