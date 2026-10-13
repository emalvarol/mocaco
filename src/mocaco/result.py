"""Module to format Result output from convergence methods."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    import pandas as pd


class ResultPlotter:
    """Helper class to provide plotting capabilities for ConvergenceResult and GroupedConvergenceResult."""

    def __init__(self, result: ConvergenceResult | GroupedConvergenceResult) -> None:
        self.result = result

    def evolution(
        self,
        *,
        show: bool = False,
    ) -> Any:
        """
        Plot the evolution of the estimate, the error band, and the convergence point.

        Requires `matplotlib` to be installed.

        Parameters
        ----------
        show
            If True, automatically displays the plot with `plt.show()` and cleans up resources.

        Returns
        -------
        matplotlib.axes.Axes
            The matplotlib Axes object containing the plot.
        """
        # 1. Guard against direct plotting on a GroupedConvergenceResult
        if isinstance(self.result, GroupedConvergenceResult):
            available_groups = [dict(k) for k in self.result]
            raise TypeError(
                "Direct evolution plotting on a GroupedConvergenceResult is not supported without selecting a specific group. "
                "Please index a specific group first, for example: "
                "result[key].plot.evolution()\n"
                f"Available groups: {available_groups}"
            )

        # 2. Check matplotlib dependency
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "Plotting requires matplotlib. Install it via 'uv pip install mocaco[plot]'."
            ) from exc

        df = self.result.data

        # Ensure required columns exist
        missing = [
            col
            for col in (
                self.result.estimate_col,
                self.result.error_col,
                self.result.n_col,
                self.result.is_converged_col,
            )
            if col not in self.result.data.columns
        ]
        if missing:
            raise ValueError(f"Columns not found in diagnostic data for plotting: {missing}")

        # Extract arrays
        n_vals = df.get_column(self.result.n_col).to_numpy()
        estimate_vals = df.get_column(self.result.estimate_col).to_numpy()
        error_vals = df.get_column(self.result.error_col).to_numpy()

        fig, ax = plt.subplots(figsize=(8, 5))

        # Plot estimate line
        ax.plot(n_vals, estimate_vals, label="Estimate", color="#1f77b4", linewidth=2)

        # Plot error band
        ax.fill_between(
            n_vals,
            estimate_vals - error_vals,
            estimate_vals + error_vals,
            color="#1f77b4",
            alpha=0.2,
            label="Error Band",
        )

        # Plot vertical line for convergence (first True occurrence)
        converged_df = df.filter(pl.col(self.result.is_converged_col))
        if not converged_df.is_empty():
            first_converged_n = converged_df.get_column(self.result.n_col)[0]
            ax.axvline(
                x=first_converged_n,
                color="red",
                linestyle="--",
                label=f"Converged at n={first_converged_n}",
            )

        ax.set_xlabel("Number of samples (n)")
        ax.set_ylabel("Estimate")
        ax.set_title(f"Convergence Evolution ({self.result.method})")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.7)

        if show:
            plt.show()
            plt.close(fig)

        return ax

    """
    def evolution_old(
        self,
        *,
        show: bool = False,
    ) -> Any:
        ""
        Plot the evolution of the estimate, the error band, and the convergence point.

        Requires `matplotlib` to be installed.

        Parameters
        ----------
        show
            If True, automatically displays the plot with `plt.show()` and cleans up resources.

        Returns
        -------
        matplotlib.axes.Axes
            The matplotlib Axes object containing the plot.
        ""
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "Plotting requires matplotlib. Install it via 'uv pip install mocaco[plot]'."
            ) from exc

        df = self.result.data

        # Ensure required columns exist
        missing = [
            col
            for col in (
                self.result.estimate_col,
                self.result.error_col,
                self.result.n_col,
                self.result.is_converged_col,
            )
            if col not in self.result.data.columns
        ]
        if missing:
            raise ValueError(f"Columns not found in diagnostic data for plotting: {missing}")

        # Extract arrays
        n_vals = df.get_column(self.result.n_col).to_numpy()
        estimate_vals = df.get_column(self.result.estimate_col).to_numpy()
        error_vals = df.get_column(self.result.error_col).to_numpy()

        fig, ax = plt.subplots(figsize=(8, 5))

        # Plot estimate line
        ax.plot(n_vals, estimate_vals, label="Estimate", color="#1f77b4", linewidth=2)

        # Plot error band
        ax.fill_between(
            n_vals,
            estimate_vals - error_vals,
            estimate_vals + error_vals,
            color="#1f77b4",
            alpha=0.2,
            label="Error Band",
        )

        # Plot vertical line for convergence (first True occurrence)
        converged_df = df.filter(pl.col(self.result.is_converged_col))
        if not converged_df.is_empty():
            first_converged_n = converged_df.get_column(self.result.n_col)[0]
            ax.axvline(
                x=first_converged_n,
                color="red",
                linestyle="--",
                label=f"Converged at n={first_converged_n}",
            )

        ax.set_xlabel("Number of samples (n)")
        ax.set_ylabel("Estimate")
        ax.set_title(f"Convergence Evolution ({self.result.method})")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.7)

        if show:
            plt.show()
            plt.close(fig)

        return ax
    """


@dataclass(frozen=True)
class ConvergenceResult:
    """
    Common result returned by convergence criteria.

    Parameters
    ----------
    method
        Name of the convergence criterion.
    n
        Number of samples used in the final estimate.
    n_col
        Name of the n column set on the method data output
    estimate
        Final estimate of the target quantity.
    estimate_col
        Name of the estimate column set on the method data output
    error
        Final estimated error.
    error_col
        Name of the error column set on the method data output
    is_converged
        Whether the final evaluated state satisfies the criterion.
    is_converged_col
        Name of the is_converged column set on the method data output
    execution_time_sec
        Execution time consumed by the method
    data
        Full diagnostic DataFrame generated by the method/wrapper.
    diagnostics
        Method-specific diagnostic information.
    """

    # Common outputs to all criterions
    method: str
    n: int
    n_col: str
    estimate: float | None
    estimate_col: str
    error: float | None
    error_col: str
    is_converged: bool | None
    is_converged_col: str

    # Build by Wrapper or by the criterion default
    data: pl.DataFrame

    # Performance
    execution_time_sec: float | None = None

    # Method-specific outputs
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def plot(self) -> ResultPlotter:
        """Access the plotting API for this result."""
        return ResultPlotter(self)

    def __getitem__(self, key: Any) -> ConvergenceResult:
        """Subscript lookup guard for un-grouped results."""
        raise TypeError(
            f"'{type(self).__name__}' object is not subscriptable. "
            "Group-based indexing is only available when 'group_cols' is specified."
        )

    def to_polars(self) -> pl.DataFrame:
        """Return the complete diagnostic DataFrame as a Polars DataFrame."""
        return self.data

    def to_pandas(self) -> pd.DataFrame:
        """Return the complete diagnostic DataFrame as a Pandas DataFrame."""
        return self.data.to_pandas()

    def summary(self) -> None:
        """Print a rich formatted summary of the convergence result to the console."""
        console = Console()

        # Define status colors and icons
        status_color = "green" if self.is_converged else "yellow"
        status_icon = "✔" if self.is_converged else "⚠"
        status_text = "Converged" if self.is_converged else "Not Converged"

        # Create the inner layout table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[bold]Method:[/bold]", f"[cyan]{self.method}[/cyan]")
        table.add_row(
            "[bold]Status:[/bold]", f"[{status_color}]{status_icon} {status_text}[/{status_color}]"
        )
        table.add_row("[bold]Samples (n):[/bold]", str(self.n))
        est_str = f"{self.estimate:.6g}" if self.estimate is not None else "-"
        table.add_row("[bold]Estimate:[/bold]", est_str)
        err_str = f"{self.error:.6g}" if self.error is not None else "-"
        table.add_row("[bold]Error:[/bold]", err_str)
        if self.execution_time_sec is not None:
            table.add_row(
                "[bold]Execution Time:[/bold]", f"{self.execution_time_sec * 1000:.2f} ms"
            )

        # Append diagnostics dynamically if they exist
        if self.diagnostics:
            table.add_row("", "")  # Spacer
            table.add_row("[bold italic]Diagnostics:[/bold italic]", "")
            for key, value in self.diagnostics.items():
                # Format floats cleanly, otherwise just cast to str
                val_str = f"{value:.6g}" if isinstance(value, float) else str(value)
                table.add_row(f"  {key}:", val_str)

        # Wrap in a stylized panel
        panel = Panel(
            table,
            title="[bold]Convergence Summary[/bold]",
            title_align="left",
            border_style=status_color,
            expand=False,
        )

        console.print()
        console.print(panel)
        console.print()

    def __str__(self) -> str:
        """Return the string representation of the underlying Polars DataFrame."""
        return str(self.data)

    def __repr__(self) -> str:
        """Return a compact string representation of the result summary."""
        return (
            f"ConvergenceResult("
            f"method={self.method!r}, "
            f"n={self.n!r}"
            f"estimate={self.estimate!r}, "
            f"error={self.error!r}, "
            f"is_converged={self.is_converged!r}, "
            f")"
        )


class GroupedConvergenceResult(dict[tuple[tuple[str, Any], ...], ConvergenceResult]):
    """
    Collection of ConvergenceResults mapped by group keys.

    Inherits from dict while exposing combined result properties and metrics.
    """

    @property
    def plot(self) -> ResultPlotter:
        """Access the plotting API for this grouped result collection."""
        return ResultPlotter(self)

    @property
    def n(self) -> int:
        """Total number of samples evaluated across all groups."""
        return sum(res.n for res in self.values())

    @property
    def error(self) -> float | None:
        """
        Absolute sum of the errors across all evaluated groups.

        Returns None if no groups have an error calculated.
        """
        errors = [abs(res.error) for res in self.values() if res.error is not None]
        return sum(errors) if errors else None

    @property
    def estimate(self) -> float | None:
        """Raises TypeError. Estimates cannot be generically aggregated across groups."""
        raise TypeError(
            "Cannot access 'estimate' directly on a GroupedConvergenceResult. "
            "You must index a specific group first, for example: result[group_key].estimate"
        )

    @property
    def diagnostics(self) -> dict[str, Any]:
        """Raises TypeError. Diagnostics are specific to each group."""
        raise TypeError(
            "Cannot access 'diagnostics' directly on a GroupedConvergenceResult. "
            "You must index a specific group first, for example: result[group_key].diagnostics"
        )

    @property
    def is_converged(self) -> bool:
        """Return True if all groups have converged."""
        return all(res.is_converged for res in self.values())

    @property
    def data(self) -> pl.DataFrame:
        """Combine diagnostic DataFrames from all groups into a single long-format Polars DataFrame."""
        dfs = []
        for group_key, res in self.items():
            # Attach group column key-values directly to the group DataFrame
            group_attrs = dict(group_key)
            df_group = res.data.with_columns(
                [pl.lit(val).alias(col) for col, val in group_attrs.items()]
            )
            dfs.append(df_group)

        return pl.concat(dfs) if dfs else pl.DataFrame()

    @property
    def execution_time_sec(self) -> float | None:
        """Return the total execution time across all evaluated groups."""
        times = [
            res.execution_time_sec for res in self.values() if res.execution_time_sec is not None
        ]
        return sum(times) if times else None

    def to_polars(self) -> pl.DataFrame:
        """Return the combined diagnostic DataFrame across all groups as a Polars DataFrame."""
        return self.data

    def to_pandas(self) -> pd.DataFrame:
        """Return the combined diagnostic DataFrame across all groups as a Pandas DataFrame."""
        return self.data.to_pandas()

    def summary(self) -> None:
        """Print formatted summaries for all individual groups."""
        for group_key, res in self.items():
            group_str = ", ".join(f"{col}={val}" for col, val in group_key)
            print(f"\n--- Group ({group_str}) ---")
            res.summary()
