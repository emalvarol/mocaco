from ..registry import registry
from .clt_absolute import CLTAbsoluteCriterion

registry.register(
    CLTAbsoluteCriterion()
)

__all__ = [
    "CLTAbsoluteCriterion",
]
