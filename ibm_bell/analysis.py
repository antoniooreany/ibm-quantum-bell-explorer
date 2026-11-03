def compute_expectation(counts: dict[str, int]) -> float:
    """Compute expectation value <AB> from Qiskit counts.
    The bitstring format follows Qiskit's little‑endian convention:
    - index 0 = most‑significant bit (Bob)
    - index 1 = least‑significant bit (Alice)
    """
    total = sum(counts.values())
    exp = 0.0
    for bits, cnt in counts.items():
        a = 1 if bits[1] == '0' else -1
        b = 1 if bits[0] == '0' else -1
        exp += a * b * cnt
    return exp / total if total else 0.0
