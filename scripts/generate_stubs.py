# Manual run:
# python scripts/generate_stubs.py

from pathlib import Path
from mocaco.registry import registry

def generate_api_stub():
    stub_lines = [
        "from __future__ import annotations",
        "",
        "import polars as pl",
        "from .protocols import SampleFrame",
        "from .result import ConvergenceResult",
        "",
        "def samples(df: pl.DataFrame, *, it_col: str | None, target_col: str) -> SampleFrame: ...",
        "def methods() -> tuple[str, ...]: ...",
        "def describe(method: str) -> dict: ...",
        "",
        "class Convergence:",
        '    def __call__(self, samples: SampleFrame, *, method: str, **kwargs) -> ConvergenceResult: ...'
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
                doc_params.append(f"        {field_name} : {field_type}\n            {field_info.description}")
            else:
                default_val = repr(field_info.default)
                args.append(f"{field_name}: {field_type} = {default_val}")
                doc_params.append(f"        {field_name} : {field_type}, default {default_val}\n            {field_info.description}")
        
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