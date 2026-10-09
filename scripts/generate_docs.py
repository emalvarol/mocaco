"""Module to generate the automatic documentation."""
# Manual run:
# python scripts/generate_docs.py

import argparse
import shutil
import subprocess
from pathlib import Path

import yaml

from mocaco.registry import registry


def load_config(config_path: str) -> dict:
    """Load the YAML configuration file."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_docs_dir_with_ruff(docs_dir: Path) -> None:
    """Format generated markdown files using Ruff if available."""
    ruff_bin = shutil.which("ruff")
    if not ruff_bin:
        print("Warning: ruff executable not found. Skipping docs formatting.")
        return

    # Formats docstrings and code blocks embedded inside generated Markdown
    subprocess.run([ruff_bin, "format", str(docs_dir)], check=False)


def _format_param_table(criterion) -> str:
    params_type = criterion.params_type
    if not hasattr(params_type, "model_fields"):
        return ""

    lines = [
        "| Parameter | Type | Default | Description |",
        "|-----------|------|---------|-------------|",
    ]

    # 1. Add Pydantic fields
    for field_name, field_info in params_type.model_fields.items():
        default = "*required*" if field_info.is_required() else f"`{field_info.default!r}`"
        # Get clean type name instead of <class 'type'>
        type_name = getattr(field_info.annotation, "__name__", str(field_info.annotation))
        desc = field_info.description or ""

        lines.append(f"| `{field_name}` | `{type_name}` | {default} | {desc} |")

    # 2. Inject Wrapper parameters if supported
    if getattr(criterion, "supports_eval_frequency", False):
        lines.append(
            "| `eval_frequency` | `int` | `None` | "
            "Number of rows between successive evaluations (handled via Wrapper). |"
        )

    return "\n".join(lines)


def _generate_method_page(name: str, criterion) -> str:
    lines = [
        f"# {name}",
        "",
        criterion.description,
        "",
        "## Parameters",
        "",
        _format_param_table(criterion),
        "",
        "## Assumptions",
        "",
    ]
    for assumption in criterion.assumptions:
        lines.append(f"- {assumption}")

    lines.extend(["", "## Limitations", ""])
    for limitation in criterion.limitations:
        lines.append(f"- {limitation}")

    lines.extend(
        [
            "",
            "## Result Interpretation",
            "",
            criterion.result_interpretation,
            "",
            "## Example Usage",
            "",
            "```python",
            criterion.example_usage,
            "```",
            "",
            "## References",
            "",
        ]
    )
    for ref in criterion.references:
        lines.append(f"- {ref}")

    lines.append("")
    return "\n".join(lines)


def generate_method_docs(docs_dir: Path):
    """Generate automatically the method documentation."""
    docs_dir.mkdir(parents=True, exist_ok=True)

    for name in registry.names():
        criterion = registry.get(name)
        content = _generate_method_page(name, criterion)
        output_path = docs_dir / f"{name}.md"
        output_path.write_text(content, encoding="utf-8")
        print(f"Generated {output_path}")


def generate_index_page():
    """Generate automatically the page index."""
    lines = [
        "# Convergence Methods",
        "",
        "Available convergence criteria in mocaco:",
        "",
    ]

    for name in registry.names():
        criterion = registry.get(name)
        # Fix the relative link since this file will now live inside docs/methods/
        lines.append(f"- [`{name}`]({name}.md) — {criterion.description}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Run all the pipeline."""
    parser = argparse.ArgumentParser(description="Generate method documentation")
    parser.add_argument(
        "--config",
        default="scripts/generate_config.yaml",
        help="Path to the generation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    docs_dir = Path(config["docs"]["output_dir"])

    generate_method_docs(docs_dir)

    index_content = generate_index_page()
    index_path = docs_dir / "index.md"
    index_path.write_text(index_content, encoding="utf-8")
    print(f"Generated {index_path}")

    format_docs_dir_with_ruff(docs_dir)


if __name__ == "__main__":
    main()
