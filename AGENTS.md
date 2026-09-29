# Role

You are a agent with expert on python but align with the developer rules of this repository:

1. Read always the contitution.md and the main_spec.md before any modification.
2. If user mention a task they are in roadmap.md Only user modify this file. Do not add new points.
3. Do not commit your modifications. User must review the changes, accept them and commit them. Commit only if user request it explicitly and clearly
4. Ask any clarification before doing changes if the user do not provide enough instructions.
5. Despite test are part of the constitution, add them only under user requests
6. Do not modify the pyproject.toml file except if user request it explicitly.
7. Run `uv run ruff check --fix . && uv run ruff format .` after each modification to verify "All checks passed!"
