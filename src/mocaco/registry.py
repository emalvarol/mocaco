"""Registry of mocaco convergence methods."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, overload

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Callable

    from .protocols import Criterion

C = TypeVar("C", bound=type)

console = Console()


class CriterionRegistry:
    def __init__(self) -> None:
        self._criteria: dict[str, Criterion] = {}

    # Overload 1: Decorator usage (no criterion provided)
    @overload
    def register(self, criterion: None = None, *, overwrite: bool = False) -> Callable[[C], C]: ...

    # Overload 2: Programmatic usage (criterion instance provided)
    @overload
    def register(self, criterion: Criterion, *, overwrite: bool = False) -> Criterion: ...

    def register(
        self,
        criterion: Criterion | None = None,
        *,
        overwrite: bool = False,
    ) -> Any:
        # 1. Programmatic use: registry.register(MyCriterion())
        if criterion is not None:
            name = criterion.name

            if not name:
                raise ValueError("A criterion must define a non-empty name.")

            if name in self._criteria and not overwrite:
                raise ValueError(f"Criterion {name!r} is already registered.")

            self._criteria[name] = criterion
            return criterion

        # 2. Decorator use: @registry.register()
        def wrapper(cls: C) -> C:
            instance = cls()
            self.register(instance, overwrite=overwrite)
            return cls

        return wrapper

    def get(self, name: str) -> Criterion:
        try:
            return self._criteria[name]
        except KeyError as exc:
            available = ", ".join(self.names())
            raise ValueError(
                f"Unknown convergence criterion: {name!r}. Available criteria: {available}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._criteria.keys())

    def describe(self, name: str) -> None:
        # 1. Fetch the criterion from the registry
        try:
            criterion = registry.get(name)
        except KeyError:
            console.print(f"[bold red]Error:[/bold red] Method '{name}' not found in registry.")
            return

        # 2. Print the Method Name and Main Description in a Panel
        console.print()
        console.print(
            Panel(
                f"{criterion.description}",
                title=f"Method: [bold cyan]{name}[/bold cyan]",
                title_align="left",
                border_style="cyan",
                expand=False,
            )
        )

        # 3. Create a Table for the Parameters
        table = Table(
            title="Parameters",
            title_style="bold magenta",
            title_justify="left",
            show_header=True,
            header_style="bold black on white",
        )

        table.add_column("Name", style="bold cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Required", justify="center")
        table.add_column("Default", style="yellow")
        table.add_column("Description", style="dim")

        # 4. Introspect the Pydantic V2 model fields
        params_type = criterion.params_type

        for field_name, field_info in params_type.model_fields.items():
            # Get type name cleanly
            field_type = getattr(field_info.annotation, "__name__", str(field_info.annotation))

            is_required = field_info.is_required()
            req_icon = "[green]✔[/green]" if is_required else "[red]✘[/red]"
            default_val = "-" if is_required else repr(field_info.default)
            desc = field_info.description or "No description provided."

            table.add_row(field_name, field_type, req_icon, default_val, desc)

        # 5. Render the table
        console.print(table)
        console.print()


registry = CriterionRegistry()
