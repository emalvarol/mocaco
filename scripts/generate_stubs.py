"""Module to generate automatic stub for methods."""
# Manual run:
# python scripts/generate_stubs.py

import inspect
import re
from pathlib import Path

from mocaco.api import describe, methods, samples
from mocaco.registry import registry


def get_function_stub(func) -> str:
    """Dynamically generates a stub line for a given function."""
    sig = inspect.signature(func)

    # str(sig) yields e.g.: (df: pl.DataFrame, *, target_col: str) -> SampleFrame
    sig_str = str(sig)

    # If the source file uses `from __future__ import annotations`, inspect
    # might wrap the type hints in single quotes. This regex safely removes
    # quotes from type hints while leaving default string values intact.
    sig_str = re.sub(r"(?<=: )'([^']+)'", r"\1", sig_str)
    sig_str = re.sub(r"(?<=-> )'([^']+)'", r"\1", sig_str)

    return f"def {func.__name__}{sig_str}: ..."


def generate_api_stub():
    """Generate api stubs."""
    stub_lines = [
        "from __future__ import annotations",
        "",
        "import polars as pl",
        "from typing import Optional, Any",  # 1. Add Any here
        "from .protocols import SampleFrame",
        "from .result import ConvergenceResult",
        "",
        get_function_stub(samples),
        get_function_stub(methods),
        get_function_stub(describe),
        "",
        "class Convergence:",
        "    def __call__(self, samples: SampleFrame, *, method: str, **kwargs: Any) -> ConvergenceResult: ...",
    ]

    # Iterate over all registered criteria
    for name in registry.names():
        criterion = registry.get(name)
        params_type = criterion.params_type

        # Build the method signature
        args = ["self", "samples: SampleFrame", "*"]
        doc_params = []

        # Introspect Pydantic V2 fields (use __fields__ for V1)
        for field_name, field_info in params_type.model_fields.items():
            field_type = field_info.annotation.__name__

            if field_info.is_required():
                args.append(f"{field_name}: {field_type}")
                doc_params.append(
                    f"        {field_name} : {field_type}\n            {field_info.description}"
                )
            else:
                default_val = repr(field_info.default)
                args.append(f"{field_name}: {field_type} = {default_val}")
                doc_params.append(
                    f"        {field_name} : {field_type}, default {default_val}\n            {field_info.description}"
                )

        supports_eval_frequency = getattr(criterion, "supports_eval_frequency", False)

        if supports_eval_frequency:
            args.append("eval_frequency: int = 1")
            doc_params.append(
                "        eval_frequency : int, default 1\n            Number of rows between successive evaluations."
            )

        signature = ", ".join(args)

        docstring = f'        """\n        {criterion.description}\n\n        Parameters\n        ----------\n'
        docstring += "\n".join(doc_params)
        docstring += '\n        """'

        stub_lines.append(f"    def {name}({signature}) -> ConvergenceResult:")
        stub_lines.append(docstring)
        stub_lines.append("        ...")

    stub_lines.append("convergence: Convergence")

    # Write to api.pyi
    output_path = Path("src/mocaco/api.pyi")
    output_path.write_text("\n".join(stub_lines))
    print(f"Successfully generated {output_path}")


if __name__ == "__main__":
    generate_api_stub()
