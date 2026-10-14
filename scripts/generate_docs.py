"""Module to generate the automatic documentation."""
# Manual run:
# python scripts/generate_docs.py

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from mocaco.registry import registry


def load_config(config_path: str) -> dict:
    """Load the YAML configuration file."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def remove_orphan_method_docs(docs_dir: Path) -> list[str]:
    """Delete .md files in docs_dir that do not correspond to a registered method."""
    registered = set(registry.names())
    removed = []
    if docs_dir.exists():
        for md_file in docs_dir.glob("*.md"):
            if md_file.stem == "index":
                continue
            if md_file.stem not in registered:
                md_file.unlink()
                removed.append(str(md_file))
                print(f"Removed orphan doc: {md_file}")
    return removed


def check_mkdocs_nav(docs_root: Path) -> list[str]:
    """Detect broken references in mkdocs.yml nav entries (md files that do not exist)."""
    mkdocs_path = docs_root.parent / "mkdocs.yml"
    if not mkdocs_path.exists():
        return []

    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8")) or {}
    nav = config.get("nav", [])
    broken = []

    def _walk(entries):
        for entry in entries:
            if isinstance(entry, dict):
                for _label, value in entry.items():
                    if isinstance(value, str) and value.endswith(".md"):
                        target = docs_root / value
                        if not target.exists():
                            broken.append(value)
                    elif isinstance(value, list):
                        _walk(value)
            elif isinstance(entry, str) and entry.endswith(".md"):
                target = docs_root / entry
                if not target.exists():
                    broken.append(entry)

    _walk(nav)
    return broken


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

    # Add Pydantic fields
    for field_name, field_info in params_type.model_fields.items():
        default = "*required*" if field_info.is_required() else f"`{field_info.default!r}`"
        # Get clean type name instead of <class 'type'>
        type_name = getattr(field_info.annotation, "__name__", str(field_info.annotation))
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


def sync_mkdocs_nav(docs_root: Path) -> None:
    """Add/remove method entries in the mkdocs.yml Methods nav section."""
    mkdocs_path = docs_root.parent / "mkdocs.yml"
    if not mkdocs_path.exists():
        print(f"Warning: {mkdocs_path} not found. Skipping nav sync.")
        return

    methods = registry.names()
    lines = mkdocs_path.read_text(encoding="utf-8").splitlines()

    methods_idx = None
    methods_indent = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "- Methods:" or stripped.startswith("- Methods:"):
            methods_indent = len(line) - len(line.lstrip())
            methods_idx = index
            break

    if methods_idx is None:
        print("Warning: no 'Methods' entry found in mkdocs.yml nav. Skipping nav sync.")
        return

    block_end = methods_idx + 1
    child_indent = methods_indent + 4
    saw_child = False
    while block_end < len(lines):
        stripped = lines[block_end].strip()
        if not stripped:
            break
        indent = len(lines[block_end]) - len(lines[block_end].lstrip())
        if indent <= methods_indent:
            break
        if not saw_child:
            child_indent = indent
            saw_child = True
        block_end += 1

    lines[methods_idx] = " " * methods_indent + "- Methods:"
    new_children = [" " * child_indent + f"- {name}: methods/{name}.md" for name in methods]
    lines[methods_idx + 1 : block_end] = new_children

    mkdocs_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Synced Methods nav in {mkdocs_path} ({len(methods)} methods)")


def copy_readme_as_home(docs_root: Path) -> None:
    """Copy README.md into the docs root as the mkdocs main page."""
    readme_source = docs_root.parent / "README.md"
    if not readme_source.exists():
        print(f"Warning: {readme_source} not found. Skipping README copy.")
        return
    dest = docs_root / "README.md"
    shutil.copy2(readme_source, dest)
    print(f"Copied {readme_source} -> {dest}")


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
    docs_root = docs_dir.parent

    remove_orphan_method_docs(docs_dir)

    copy_readme_as_home(docs_root)

    generate_method_docs(docs_dir)

    sync_mkdocs_nav(docs_root)

    broken_nav = check_mkdocs_nav(docs_root)
    if broken_nav:
        for ref in broken_nav:
            print(
                f"ERROR: Broken mkdocs.yml nav reference: {ref} (file does not exist)",
                file=sys.stderr,
            )
        sys.exit(1)

    format_docs_dir_with_ruff(docs_dir)


if __name__ == "__main__":
    main()
