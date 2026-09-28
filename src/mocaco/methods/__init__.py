from ..registry import registry
from .clt_absolute import CLTAbsoluteCriterion, clt_absolute

registry.register(
    CLTAbsoluteCriterion()
)

__all__ = [
    "CLTAbsoluteCriterion",
    "clt_absolute",
]
