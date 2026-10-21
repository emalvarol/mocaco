# Role
You are an expert python agent aligned with the developer rules of this repository:

# Rule
1. Read always the contitution.md and the main_spec.md before any modification.
2. If user mention a task, they are in roadmap.md Only user modify this file. Do not add new points.
3. Do not commit your modifications. User must review the changes, accept them and commit them. Commit only if user request it explicitly and clearly
4. Ask any clarification before doing changes if the user do not provide enough instructions.
5. Despite test are part of the constitution, add them only under user requests
6. Do not modify the pyproject.toml file except if user request it explicitly.
7. Run `uv run ruff check --fix . && uv run ruff format .` to verify "All checks passed!" AND `uv run mypy src/` to verify "Sucess: no issues found in..." after each modification.

# Environment stack
- The repository use a virtual environment created with `uv`.
- The repository use ruff and ty for checking.

### mypy
```bash
uv run mypy src/
```

# Pi Agent Context
If you are a Pi Agent consider this to avoid errors while working:
- Prioritize your tools read, write, edit and bash.
- Use python -c "..." to avoid the shell fork issue
- Use python one-liners for file exploration (os.listdir, glob, pathlib)
- Run scripts with python script.py instead of relying on shell commands
