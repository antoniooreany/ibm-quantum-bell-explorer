import numpy as np
from qiskit import QuantumCircuit

def create_chsh_circuit(theta_a: float, theta_b: float) -> QuantumCircuit:
    """Generate the standard CHSH circuit for the given measurement angles.
    Returns a 2‑qubit circuit with measurement.
    """
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(theta_a, 0)
    qc.ry(theta_b, 1)
    qc.measure([0, 1], [0, 1])
    return qc
