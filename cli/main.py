"""Command‑line interface for the IBM Quantum Bell experiment.

Provides a single entry point `ibm-bell-run` that can execute a parameter sweep
with optional noise‑mitigation and tomography.
"""
from pathlib import Path

import typer

from ibm_bell import experiment, io

app = typer.Typer(add_completion=False)

@app.command()
def run(
    shots: int = 1024,
    grid_a: int = 5,
    grid_b: int = 5,
    backend: str = typer.Option(None, "--backend", help="Force a specific IBM Quantum backend name"),
    mitigation: list[str] = typer.Option(None, "--mitigation", help="Mitigation techniques (e.g., zne, readout)"),
    tomography: bool = False,
    output: Path = Path("results/grid.csv"),
):
    """Run a CHSH parameter sweep.

    Args:
        shots: Number of shots per circuit.
        grid_a: Number of points for Alice's angle grid.
        grid_b: Number of points for Bob's angle grid.
        backend: Optional specific backend name.
        mitigation: List of mitigation technique names.
        tomography: Whether to perform state tomography after the sweep.
        output: Path where the resulting grid will be saved (CSV by default).
    """
    # Generate equally spaced angles between 0 and pi/2
    angles_a = [i * 3.141592653589793 / (grid_a - 1) for i in range(grid_a)]
    angles_b = [i * 3.141592653589793 / (grid_b - 1) for i in range(grid_b)]
    cfg = experiment.SweepConfig(
        angles_a=angles_a,
        angles_b=angles_b,
        shots=shots,
        mitigation=mitigation,
        tomography=tomography,
    )
    grid, backend_name = experiment.run_sweep(cfg, backend_name=backend)
    saved_path = io.save_grid(grid, output)
    typer.echo(f"Sweep completed on backend {backend_name}. Grid saved to {saved_path} (and {output})")

if __name__ == "__main__":
    app()
