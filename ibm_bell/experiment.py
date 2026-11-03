"""High‑level experiment orchestration for the IBM Quantum Bell CHSH experiment.

Provides:
- Parameter sweep over measurement angles.
- Optional noise‑mitigation (placeholders for Zero‑Noise Extrapolation, Readout Mitigation).
- Optional state tomography.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from .analysis import compute_expectation
from .circuits import create_chsh_circuit
from .service import get_service

# Placeholder imports for mitigation – actual implementations would use Qiskit Ignis or Mitigation classes.
# from qiskit_ignis.mitigation import CompleteMeasFitter, ZeroNoiseExtrapolation

@dataclass
class SweepConfig:
    """Configuration for a parameter sweep.

    Attributes
    ----------
    angles_a: Sequence[float]
        List of Alice measurement angles (radians).
    angles_b: Sequence[float]
        List of Bob measurement angles (radians).
    shots: int, default 1024
        Number of shots for each circuit.
    mitigation: Optional[Sequence[str]]
        List of mitigation techniques to apply (e.g., "zne", "readout").
    tomography: bool, default False
        Whether to perform state tomography after the sweep.
    """

    angles_a: Sequence[float]
    angles_b: Sequence[float]
    shots: int = 1024
    mitigation: Optional[Sequence[str]] = None
    tomography: bool = False

def _apply_mitigation(circuits: List, techniques: Sequence[str]):
    """Placeholder for applying mitigation techniques to a list of circuits.
    In a full implementation this would wrap each circuit with the appropriate Qiskit
    error‑mitigation primitives.
    """
    # For now we simply return the circuits unchanged.
    return circuits

def run_sweep(cfg: SweepConfig, backend_name: str | None = None):
    """Run a CHSH parameter sweep.

    Parameters
    ----------
    cfg: SweepConfig
        Configuration for the sweep.
    backend_name: str | None, optional
        Name of a specific backend to use. If omitted, the least‑busy real backend
        (operational=True, simulator=False) is selected.

    Returns
    -------
    grid: np.ndarray
        2‑D array of expectation values with shape (len(angles_a), len(angles_b)).
    backend_used: str
        Name of the backend the job was submitted to.
    """
    service = get_service()
    if backend_name:
        backend = service.backend(backend_name)
    else:
        try:
            backend = service.least_busy(operational=True, simulator=False, min_num_qubits=2)
        except Exception as e:
            # Fall back to simulator only if no operational real quantum computer is available
            print(f"Warning: Real quantum computer unavailable ({e}). Falling back to simulator.")
            try:
                backend = service.least_busy(operational=True, simulator=True)
            except Exception:
                backend = service.backend('ibmq_qasm_simulator')

    # Build circuits for each (a, b) pair.
    circuits = [create_chsh_circuit(a, b) for a in cfg.angles_a for b in cfg.angles_b]

    # Transpile circuits to the target backend's basis gates
    from qiskit import transpile
    try:
        circuits = transpile(circuits, backend=backend, optimization_level=1)
    except Exception as transpile_err:
        if not getattr(backend, "is_simulator", False):
            print(f"Warning: Transpilation failed on real backend {backend.name}: {transpile_err}. Falling back to simulator.")
            try:
                backend = service.least_busy(operational=True, simulator=True)
            except Exception:
                backend = service.backend('ibmq_qasm_simulator')
            circuits = transpile(circuits, backend=backend, optimization_level=1)
        else:
            raise transpile_err

    if cfg.mitigation:
        circuits = _apply_mitigation(circuits, cfg.mitigation)

    from qiskit_ibm_runtime import SamplerV2 as Sampler
    try:
        sampler = Sampler(backend)
        job = sampler.run(circuits, shots=cfg.shots)
        result = job.result()
    except Exception as run_err:
        # If running on the real quantum device failed (e.g. queue/quota/access error),
        # fall back to simulator as last resort.
        if not getattr(backend, "is_simulator", False):
            print(f"Warning: Execution failed on real backend {backend.name}: {run_err}. Falling back to simulator.")
            try:
                backend = service.least_busy(operational=True, simulator=True)
            except Exception:
                backend = service.backend('ibmq_qasm_simulator')
            circuits = transpile(circuits, backend=backend, optimization_level=1)
            sampler = Sampler(backend)
            job = sampler.run(circuits, shots=cfg.shots)
            result = job.result()
        else:
            raise run_err

    expectations = [compute_expectation(r.data.c.get_counts()) for r in result]
    grid = np.array(expectations).reshape(len(cfg.angles_a), len(cfg.angles_b))

    # Optional tomography – placeholder implementation.
    if cfg.tomography:
        # In a full implementation this would call a tomography routine on the
        # Bell state prepared by the first circuit.
        pass

    return grid, backend.name
