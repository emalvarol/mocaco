"""Module to format Result output from convergence methods."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, overload

import polars as pl
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    import pandas as pd


type GroupKey = tuple[tuple[str, Any], ...]


class GroupKeyMapping[V](dict[GroupKey, V]):
    """
    Mapping keyed by group keys that accepts multiple lookup formats.

    Lookups support:
      1. Canonical tuple-of-pairs key: mapping[(("group", "group_a"),)]
      2. Dict selector (order-independent): mapping[{"group": "group_a"}]
      3. Scalar or Tuple of values (positional): mapping["group_a"] or mapping["A", "B"]
    """

    @overload
    def __getitem__(self, key: GroupKey) -> V: ...

    @overload
    def __getitem__(self, key: Mapping[str, Any]) -> V: ...

    @overload
    def __getitem__(self, key: tuple[Any, ...]) -> V: ...

    @overload
    def __getitem__(self, key: str | int | float) -> V: ...

    def __getitem__(self, key: Any) -> V:
        """Return the value for a canonical key, dict selector, or value tuple."""
        # 1. Dictionary / Mapping selector (checked first because dicts are unhashable)
        if isinstance(key, Mapping):
            resolved_key = self._resolve_dict_key(key)
            return super().__getitem__(resolved_key)

        # 2. Direct match (Canonical GroupKey)
        try:
            if key in self:
                return super().__getitem__(key)
        except TypeError:
            pass

        # 3. Scalar or Value Tuple selector
        resolved_key = self._resolve_value_key(key)
        return super().__getitem__(resolved_key)

    @property
    def _group_columns(self) -> tuple[str, ...]:
        """Extract the ordered list of group column names from the mapping keys."""
        if not self:
            raise KeyError("No groups available.")
        return tuple(col for col, _ in next(iter(self)))

    def _resolve_dict_key(self, selector: Mapping[str, Any]) -> GroupKey:
        """Translate a dict selector into the canonical tuple-of-pairs group key."""
        columns = self._group_columns
        missing = [col for col in columns if col not in selector]
        extra = [col for col in selector if col not in columns]
        if missing or extra:
            raise ValueError(
                f"Group selector must specify exactly the group columns {list(columns)}; "
                f"got {sorted(selector)} (missing={missing}, unknown={extra})."
            )
        return tuple((col, selector[col]) for col in columns)

    def _resolve_value_key(self, key: Any) -> GroupKey:
        """Translate a scalar or value tuple into the canonical tuple-of-pairs group key."""
        columns = self._group_columns

        # If it's a single scalar value, wrap it in a tuple
        if not isinstance(key, tuple):
            key = (key,)

        if len(key) != len(columns):
            raise ValueError(
                f"Expected {len(columns)} value(s) for group columns {list(columns)}; "
                f"got {len(key)} value(s) ({key})."
            )
        return tuple((col, val) for col, val in zip(columns, key, strict=True))


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

    def residual_error_evolution(
        self,
        *,
        keep: str | list[str],
        filter: Mapping[str, Any] | None = None,
        show: bool = False,
    ) -> Any:
        """
        Plot the evolution of the aggregated residual error across iterations.

        Only available for grouped results. It delegates to
        :meth:`GroupedConvergenceResult.data_residual_error_by` to obtain the data,
        then draws one ``res_error`` curve per unique combination of the kept group
        columns, with a vertical line at the last iteration where ``is_converged`` is
        True. The y-axis starts at 0 and is capped at the largest residual found.

        Requires `matplotlib` to be installed.

        Parameters
        ----------
        keep
            Group column name, or list of names, kept as distinct curves.
        filter
            Optional dict selector restricting the plotted kept groups, e.g.
            ``{"cat1": "A"}`` or ``{"cat1": ["A", "B"]}``.
        show
            If True, automatically displays the plot with `plt.show()` and cleans up resources.

        Returns
        -------
        matplotlib.axes.Axes
            The matplotlib Axes object containing the plot.
        """
        # 1. Only grouped results are supported for now
        if not isinstance(self.result, GroupedConvergenceResult):
            raise TypeError(
                "residual_error_evolution is only available for grouped results "
                "(created with 'group_cols')."
            )

        # 2. Check matplotlib dependency
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "Plotting requires matplotlib. Install it via 'uv pip install mocaco[plot]'."
            ) from exc

        keep_cols = [keep] if isinstance(keep, str) else list(keep)
        df = self.result.data_residual_error_by(keep=keep_cols, filter=filter)
        if df.is_empty():
            raise ValueError(
                "No residual evolution data to plot for the given 'keep' and 'filter'."
            )

        n_col = self.result.n_col
        is_converged_col = self.result.is_converged_col

        fig, ax = plt.subplots(figsize=(8, 5))

        combos = df.select(keep_cols).unique(maintain_order=True).iter_rows(named=True)
        for combo in combos:
            subset = df.filter([pl.col(col) == value for col, value in combo.items()])
            n_vals = subset.get_column(n_col).to_numpy()
            residual_vals = subset.get_column("res_error").to_numpy()
            label = ", ".join(f"{col}={value}" for col, value in combo.items())

            (line,) = ax.plot(n_vals, residual_vals, marker="o", label=label)

            converged = subset.filter(pl.col(is_converged_col))
            if not converged.is_empty():
                last_converged_n = converged.get_column(n_col)[-1]
                ax.axvline(
                    x=last_converged_n,
                    color=line.get_color(),
                    linestyle="--",
                    alpha=0.7,
                )

        max_residual = float(df.get_column("res_error").max())  # type: ignore[arg-type]
        ax.set_ylim(bottom=0, top=max(max_residual, 1e-12))

        ax.set_xlabel("Number of samples (n)")
        ax.set_ylabel("Residual error")
        ax.set_title("Residual Error Evolution")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.7)

        if show:
            plt.show()
            plt.close(fig)

        return ax


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
    residual_error
        Residual error left above the stopping threshold, i.e.
        ``max(0, |error| - threshold)``. It is ``None`` when the criterion does
        not expose an error or a threshold.
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

    # Residual error remaining above the stopping threshold: max(0, |error| - threshold)
    residual_error: float | None = None

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
            f"n={self.n!r}, "
            f"estimate={self.estimate!r}, "
            f"error={self.error!r}, "
            f"is_converged={self.is_converged!r}, "
            f")"
        )

    def error_by(self, *, keep: str | list[str]) -> GroupKeyMapping[float | None]:
        """
        Return residual absolute error aggregated over group columns not in `keep`.

        This method is only applicable when the result was obtained with ``group_cols``
        specified. Without grouping, all errors are aggregated into a single value.

        Parameters
        ----------
        keep
            Group column name, or list of names, to keep as distinct entries.

        Returns
        -------
        GroupKeyMapping[float | None]
            Mapping from the kept group key to its aggregated absolute error.

        Raises
        ------
        TypeError
            Always raised, as this method is only applicable when ``group_cols`` was used.
        """
        raise TypeError(
            "Cannot access 'error_by' on a ConvergenceResult without grouping. "
            "Group-based error aggregation is only available when 'group_cols' is specified. "
            "Please index a specific group first, for example: result[group_key].error_by(...)"
        )

    def residual_error_by(self, *, keep: str | list[str]) -> GroupKeyMapping[float | None]:
        """
        Return residual error aggregated over group columns not in `keep`.

        This method is only applicable when the result was obtained with ``group_cols``
        specified.

        Raises
        ------
        TypeError
            Always raised, as this method is only applicable when ``group_cols`` was used.
        """
        raise TypeError(
            "Cannot access 'residual_error_by' on a ConvergenceResult without grouping. "
            "Group-based residual aggregation is only available when 'group_cols' is specified. "
            "Please index a specific group first, for example: "
            "result[group_key].residual_error_by(...)"
        )

    def data_residual_error_by(
        self,
        *,
        keep: str | list[str],
        filter: Mapping[str, Any] | None = None,
    ) -> pl.DataFrame:
        """
        Return the evolution of the aggregated residual error over iterations.

        This method is only applicable when the result was obtained with ``group_cols``
        specified.

        Raises
        ------
        TypeError
            Always raised, as this method is only applicable when ``group_cols`` was used.
        """
        raise TypeError(
            "Cannot access 'data_residual_error_by' on a ConvergenceResult without grouping. "
            "Group-based residual evolution is only available when 'group_cols' is specified. "
            "Please index a specific group first, for example: "
            "result[group_key].data_residual_error_by(...)"
        )


class GroupedConvergenceResult(GroupKeyMapping[ConvergenceResult]):
    """
    Collection of ConvergenceResults mapped by group keys.

    Inherits from dict while exposing combined result properties and metrics.

    Individual groups can be selected in three intuitive ways:

        result["group_a"]                   # 1. Scalar/Tuple value lookup
        result[{"group": "group_a"}]        # 2. Dict selector
        result[(("group", "group_a"),)]     # 3. Canonical key
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
    def n_col(self) -> str:
        """Name of the n column set on the method data output."""
        return next(iter(self.values())).n_col

    @property
    def error(self) -> float | None:
        """
        Residual absolute sum of the errors across all evaluated groups.

        Returns None if no groups have an error calculated.
        """
        errors = [abs(res.error) for res in self.values() if res.error is not None]
        return sum(errors) if errors else None

    def error_by(self, *, keep: str | list[str]) -> GroupKeyMapping[float | None]:
        """
        Aggregate the residual absolute error over a subset of the grouping dimensions.

        Groups are collapsed (marginalized) over every group column not listed in
        ``keep``; the absolute errors of the collapsed groups are summed into a
        residual absolute sum. This allows selective, partial aggregation of grouped
        results.

        Parameters
        ----------
        keep
            Group column name, or list of names, to keep as distinct entries in the
            returned mapping. Every other group column is aggregated over.

        Returns
        -------
        GroupKeyMapping[float | None]
            Mapping from the kept group key to its aggregated absolute error. A key
            maps to None when none of its collapsed groups expose an error. Entries
            can be looked up seamlessly:

        Examples
        --------
        With ``group_cols=["cat1", "cat2"]``:

            errors = result.error_by(keep=["cat1"])

            # All three lookups evaluate without Pylance warnings:
            errors["A"]
            errors[{"cat1": "A"}]
            errors[(("cat1", "A"),)]
        """
        keep_cols = self._resolve_keep_cols(keep)

        aggregated: dict[GroupKey, list[float]] = {}
        for group_key, res in self.items():
            sub_key: GroupKey = tuple((col, value) for col, value in group_key if col in keep_cols)
            bucket = aggregated.setdefault(sub_key, [])
            if res.error is not None:
                bucket.append(abs(res.error))

        return GroupKeyMapping(
            {key: (sum(errors) if errors else None) for key, errors in aggregated.items()}
        )

    def residual_error_by(self, *, keep: str | list[str]) -> GroupKeyMapping[float | None]:
        """
        Aggregate the residual error over a subset of the grouping dimensions.

        Residual error is the part of the error still above the stopping threshold,
        ``max(0, |error| - threshold)``. Groups are collapsed (marginalized) over every
        group column not listed in ``keep``; their residual errors are summed. The
        aggregated residual reaches exactly ``0.0`` when every collapsed group has
        converged.

        Parameters
        ----------
        keep
            Group column name, or list of names, to keep as distinct entries in the
            returned mapping. Every other group column is aggregated over.

        Returns
        -------
        GroupKeyMapping[float | None]
            Mapping from the kept group key to its aggregated residual error. A key
            maps to None when none of its collapsed groups expose a residual. Entries
            can be looked up seamlessly:

        Examples
        --------
        With ``group_cols=["cat1", "cat2"]``:

            residuals = result.residual_error_by(keep=["cat1"])

            residuals["A"]
            residuals[{"cat1": "A"}]
            residuals[(("cat1", "A"),)]
        """
        keep_cols = self._resolve_keep_cols(keep)

        aggregated: dict[GroupKey, list[float]] = {}
        for group_key, res in self.items():
            sub_key: GroupKey = tuple((col, value) for col, value in group_key if col in keep_cols)
            bucket = aggregated.setdefault(sub_key, [])
            if res.residual_error is not None:
                bucket.append(res.residual_error)

        return GroupKeyMapping(
            {key: (sum(residuals) if residuals else None) for key, residuals in aggregated.items()}
        )

    def data_residual_error_by(
        self,
        *,
        keep: str | list[str],
        filter: Mapping[str, Any] | None = None,
    ) -> pl.DataFrame:
        """
        Return the evolution of the aggregated residual error over iterations.

        For every kept group key, the collapsed groups' per-iteration residual errors
        ``max(0, |error| - threshold)`` are summed into a ``res_error`` column, giving
        the evolution of the residual across iterations. The remaining value columns
        are aggregated with their (unweighted) arithmetic mean and renamed with an
        ``agg_`` prefix. ``is_converged`` is True when ``res_error`` reaches exactly
        ``0.0``, i.e. when every collapsed group has converged.

        The collapsed groups of a kept key must share the exact same ``n`` sequence;
        otherwise a ``ValueError`` is raised, asking the user to aggregate only groups
        evaluated on the same iterations.

        Parameters
        ----------
        keep
            Group column name, or list of names, to keep as distinct entries. Every
            other group column is aggregated over.
        filter
            Optional dict selector restricting the returned kept groups. Keys must be
            kept columns; values can be scalar or a list of accepted values, e.g.
            ``{"cat1": "A"}`` or ``{"cat1": ["A", "B"]}``.

        Returns
        -------
        pl.DataFrame
            Long-format DataFrame with the kept group columns, the ``n`` column, one
            ``agg_<column>`` per aggregated value column, ``res_error`` and
            ``is_converged``.

        Examples
        --------
        With ``group_cols=["cat1", "cat2"]``:

            evolution = result.data_residual_error_by(keep=["cat1"])
            subset = result.data_residual_error_by(keep=["cat1"], filter={"cat1": "A"})

        Raises
        ------
        ValueError
            If a kept column is unknown, if a filter key is not kept, if the collapsed
            groups do not share the same ``n`` sequence, or if a group does not expose a
            ``threshold`` diagnostic.
        """
        keep_cols = self._resolve_keep_cols(keep)
        n_col = self.n_col
        error_col = self.error_col
        is_converged_col = self.is_converged_col

        buckets: dict[GroupKey, list[ConvergenceResult]] = {}
        for group_key, res in self.items():
            if res.data.is_empty():
                continue
            sub_key: GroupKey = tuple((col, value) for col, value in group_key if col in keep_cols)
            buckets.setdefault(sub_key, []).append(res)

        if not buckets:
            return pl.DataFrame()

        first = next(iter(buckets.values()))[0]
        value_cols = [
            col for col in first.data.columns if col not in (n_col, error_col, is_converged_col)
        ]

        frames: list[pl.DataFrame] = []
        for sub_key, results in buckets.items():
            n_sequences = [res.data.get_column(n_col).to_list() for res in results]
            if any(seq != n_sequences[0] for seq in n_sequences[1:]):
                bucket_repr = dict(sub_key)
                raise ValueError(
                    f"Groups collapsed into {bucket_repr} do not share the same '{n_col}' "
                    "sequence. data_residual_error_by requires that the aggregated groups "
                    "are evaluated on identical iterations."
                )

            for res in results:
                threshold = res.diagnostics.get("threshold")
                if threshold is None:
                    raise ValueError(
                        "data_residual_error_by requires a 'threshold' diagnostic on each "
                        "group to compute the residual error, but none was found for "
                        f"{dict(sub_key)}."
                    )
                residual = (pl.col(error_col).abs() - float(threshold)).clip(lower_bound=0.0)
                df = res.data.select(
                    [pl.col(n_col), *value_cols, residual.alias("residual_error")]
                ).with_columns([pl.lit(value).alias(col) for col, value in sub_key])
                frames.append(df)

        combined = pl.concat(frames)

        aggregated = (
            combined.group_by([*keep_cols, n_col])
            .agg(
                [
                    *[pl.col(col).mean().alias(f"agg_{col}") for col in value_cols],
                    pl.col("residual_error").sum().alias("res_error"),
                ]
            )
            .with_columns((pl.col("res_error") == 0.0).alias(is_converged_col))
            .sort([*keep_cols, n_col])
        )

        result_df = aggregated.select(
            [*keep_cols, n_col, *[f"agg_{c}" for c in value_cols], "res_error", is_converged_col]
        )

        if filter is not None:
            result_df = result_df.filter(self._build_filter_mask(filter, keep_cols))

        return result_df

    @staticmethod
    def _build_filter_mask(
        filter: Mapping[str, Any],
        keep_cols: list[str],
    ) -> pl.Expr:
        """Build a Polars boolean mask from a dict selector over the kept columns."""
        unknown = [col for col in filter if col not in keep_cols]
        if unknown:
            raise ValueError(
                f"Unknown filter column(s) {sorted(unknown)}. "
                f"Filter keys must be a subset of the kept columns {keep_cols}."
            )
        conditions = [
            pl.col(col).is_in(value)
            if isinstance(value, list | tuple | set)
            else pl.col(col) == value
            for col, value in filter.items()
        ]
        return conditions[0] if len(conditions) == 1 else pl.all_horizontal(conditions)

    def _resolve_keep_cols(self, keep: str | list[str]) -> list[str]:
        """Normalize and validate the ``keep`` argument against the available group columns."""
        keep_cols = [keep] if isinstance(keep, str) else list(keep)
        available = {col for group_key in self for col, _ in group_key}
        unknown = [col for col in keep_cols if col not in available]
        if unknown:
            raise ValueError(
                f"Unknown group column(s) {unknown} for 'keep'. "
                f"Available group columns: {sorted(available)}."
            )
        return keep_cols

    @property
    def error_col(self) -> str:
        """Name of the error column set on the method data output."""
        return next(iter(self.values())).error_col

    @property
    def estimate(self) -> float | None:
        """Raises TypeError. Estimates cannot be generically aggregated across groups."""
        raise TypeError(
            "Cannot access 'estimate' directly on a GroupedConvergenceResult. "
            "You must index a specific group first, for example: result[group_key].estimate"
        )

    @property
    def estimate_col(self) -> str:
        """Name of the estimate column set on the method data output."""
        return next(iter(self.values())).estimate_col

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
    def is_converged_col(self) -> str:
        """Name of the is_converged column set on the method data output."""
        return next(iter(self.values())).is_converged_col

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
