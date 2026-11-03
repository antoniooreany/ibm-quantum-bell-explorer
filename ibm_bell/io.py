"""I/O utilities for persisting experiment results.

Provides a simple `save_grid` helper that writes a 2‑D NumPy array to CSV or JSON.
The function creates parent directories automatically and includes a timestamp in the
filename to preserve run history while optionally keeping a symlink or default copy.
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Literal
import numpy as np

def resolve_timestamped_path(path: Path | str) -> Path:
    """Append a current ISO/compact timestamp to the file name.

    For example, `results/grid.csv` -> `results/grid_20261103_211500.csv`.
    If the path already contains a timestamp or the caller specifies an exact file,
    it returns the modified Path.
    """
    p = Path(path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = p.stem
    suffix = p.suffix or ".csv"
    return p.with_name(f"{stem}_{timestamp}{suffix}")

def save_grid(
    grid: np.ndarray,
    path: Path | str,
    fmt: Literal["csv", "json"] = "csv",
    with_timestamp: bool = True,
    update_latest: bool = True,
) -> Path:
    """Save a NumPy grid to *path*.

    Parameters
    ----------
    grid: np.ndarray
        2‑D array of expectation values.
    path: Path | str
        Destination file path.
    fmt: "csv" | "json"
        Output format. Defaults to CSV.
    with_timestamp: bool, default True
        If True, save to a filename containing the current timestamp (e.g. `grid_20261103_211500.csv`).
    update_latest: bool, default True
        If True and with_timestamp is True, also write/overwrite the base path (e.g. `grid.csv`)
        so the latest run is always directly accessible.

    Returns
    -------
    actual_path: Path
        The timestamped path where the file was saved.
    """
    base_path = Path(path)
    target_path = resolve_timestamped_path(base_path) if with_timestamp else base_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    def _write(dest: Path):
        if fmt == "csv":
            with dest.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(grid)
        elif fmt == "json":
            with dest.open("w") as f:
                json.dump(grid.tolist(), f, indent=2)
        else:
            raise ValueError(f"Unsupported format {fmt!r}. Use 'csv' or 'json'.")

    _write(target_path)
    if with_timestamp and update_latest and target_path != base_path:
        _write(base_path)

    return target_path
