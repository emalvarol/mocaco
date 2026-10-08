"""Module to generate the automatic documentation."""
# Manual run:
# python scripts/generate_docs.py

from pathlib import Path

from mocaco.registry import registry


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


def generate_method_docs():
    """Generate automatically the method documentation."""
    docs_dir = Path("docs/methods")
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
    generate_method_docs()

    index_content = generate_index_page()
    # Save to docs/methods/index.md instead of docs/index.md to prevent overwriting the Home page
    index_path = Path("docs/methods/index.md")
    index_path.write_text(index_content, encoding="utf-8")
    print(f"Generated {index_path}")


if __name__ == "__main__":
    main()
