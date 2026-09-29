"""Module to generate the automatic documentation."""
# Manual run:
# python scripts/generate_docs.py

from pathlib import Path

from mocaco.registry import registry


def _format_param_table(params_type) -> str:
    if not hasattr(params_type, "model_fields"):
        return ""

    lines = [
        "| Parameter | Type | Default | Description |",
        "|-----------|------|---------|-------------|",
    ]

    for field_name, field_info in params_type.model_fields.items():
        default = "*required*" if field_info.is_required() else f"`{field_info.default!r}`"
        type_name = str(field_info.annotation)
        desc = field_info.description or ""

        lines.append(f"| `{field_name}` | `{type_name}` | {default} | {desc} |")

    return "\n".join(lines)


def _generate_method_page(name: str, criterion) -> str:
    lines = [
        f"# {name}",
        "",
        criterion.description,
        "",
        "## Parameters",
        "",
        _format_param_table(criterion.params_type),
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
        lines.append(f"- [`{name}`](methods/{name}.md) — {criterion.description}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Run all the pipeline."""
    generate_method_docs()

    index_content = generate_index_page()
    index_path = Path("docs/index.md")
    index_path.write_text(index_content, encoding="utf-8")
    print(f"Generated {index_path}")


if __name__ == "__main__":
    main()
