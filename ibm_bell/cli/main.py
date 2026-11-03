"""CLI entry point for the IBM Quantum Bell experiment.

Provides a Typer app that runs the CHSH parameter sweep.
"""

import os
import typer
from pathlib import Path
from ibm_bell import experiment, io

app = typer.Typer(add_completion=False)


@app.command()
def run(
    shots: int = 1024,
    grid_a: int = 5,
    grid_b: int = 5,
    mitigation: list[str] = typer.Option(
        None, "--mitigation", help="Mitigation techniques (e.g., zne, readout)"
    ),
    tomography: bool = False,
    output: Path = Path("results/grid.csv"),
) -> None:
    """Run the CHSH parameter sweep.

    Args:
        shots: Number of shots per circuit.
        grid_a: Number of points for Alice's angle grid.
        grid_b: Number of points for Bob's angle grid.
        mitigation: List of mitigation technique names.
        tomography: Whether to perform state tomography after the sweep.
        output: Path where the resulting grid CSV will be saved.
    """
    # Build angle grids
    angles_a = [i * 3.141592653589793 / (grid_a - 1) for i in range(grid_a)]
    angles_b = [i * 3.141592653589793 / (grid_b - 1) for i in range(grid_b)]

    cfg = experiment.SweepConfig(
        angles_a=angles_a,
        angles_b=angles_b,
        shots=shots,
        mitigation=mitigation,
        tomography=tomography,
    )

    grid, backend_name = experiment.run_sweep(cfg)
    io.save_grid(grid, output)
    typer.echo(
        f"✅ Sweep completed on backend `{backend_name}`. Grid saved to `{output}`"
    )


if __name__ == "__main__":
    app()
