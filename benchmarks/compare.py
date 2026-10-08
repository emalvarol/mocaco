"""Script to analyze benchmark results and calculate exact % improvements."""
#uv run python benchmarks/compare.py

import json
from pathlib import Path

import polars as pl
from rich.console import Console
from rich.table import Table


def analyze_benchmarks(json_path: str = "benchmarks/results.json") -> None:
    path = Path(json_path)
    if not path.exists():
        print(f"Error: No se encontró {json_path}. Ejecuta pytest con --benchmark-json primero.")
        return

    with open(path) as f:
        data = json.load(f)

    # 1. Extraer datos relevantes
    records = []
    for b in data["benchmarks"]:
        records.append({
            "n_samples": int(b["params"]["n_samples"]),
            "eval_freq": int(b["params"]["eval_freq"]),
            "implementation": b["params"]["implementation"],
            "mean_time_sec": b["stats"]["mean"],  # Tiempo medio en segundos
        })

    df = pl.DataFrame(records)

    # 2. Pivotar para poner "native" y "wrapper" en columnas separadas
    pivot_df = df.pivot(
        values="mean_time_sec",
        index=["n_samples", "eval_freq"],
        columns="implementation",
    )

    # 3. Calcular métricas de mejora
    # Porcentaje de mejora = (tiempo_lento - tiempo_rapido) / tiempo_lento * 100
    # X_times_faster = tiempo_lento / tiempo_rapido
    result_df = pivot_df.with_columns([
        ((pl.col("native2") - pl.col("native")) / pl.col("native2") * 100).alias("improvement_pct"),
        (pl.col("native2") / pl.col("native")).alias("speedup_factor"),
        (pl.col("native") < pl.col("native2")).alias("native_is_better")
    ]).sort(["n_samples", "eval_freq"])

    # 4. Imprimir tabla formateada con Rich
    console = Console()
    table = Table(title="Comparación de Rendimiento: native vs native2", header_style="bold cyan")

    table.add_column("N Samples", justify="right")
    table.add_column("Eval Freq", justify="right")
    table.add_column("Tiempo Native", justify="right", style="green")
    table.add_column("Tiempo Native2", justify="right", style="yellow")
    table.add_column("Ganador", justify="center")
    table.add_column("Mejora (%)", justify="right", style="bold green")
    table.add_column("Aceleración", justify="right", style="bold magenta")

    for row in result_df.iter_rows(named=True):
        t_native = f"{row['native'] * 1000:.2f} ms"
        t_wrapper = f"{row['native2'] * 1000:.2f} ms"
        ganador = "[green]Native[/green]" if row["native_is_better"] else "[yellow]Native2[/yellow]"
        mejora = f"{row['improvement_pct']:.1f}%"
        aceleracion = f"{row['speedup_factor']:.1f}x"

        table.add_row(
            str(row["n_samples"]),
            str(row["eval_freq"]),
            t_native,
            t_wrapper,
            ganador,
            mejora,
            aceleracion
        )

    console.print()
    console.print(table)

if __name__ == "__main__":
    analyze_benchmarks()
