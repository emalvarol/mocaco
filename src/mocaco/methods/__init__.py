"""Module to automatically expose all addded methods."""

import importlib
import pkgutil

for _finder, module_name, _ispkg in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_name}")
