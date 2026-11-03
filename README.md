# IBM Quantum Bell Explorer

A modular, test‑driven, specification‑driven Python package for running the CHSH Bell‑inequality experiment on IBM Quantum hardware (or simulators) from Google Colab, the CLI, or a lightweight web service.

## Features
- **Idempotent dependency installer** for Colab notebooks.
- **Secure token handling** via Colab Secrets or environment variables.
- **Parameter sweep** over measurement angles with optional noise‑mitigation.
- **State tomography** utilities.
- **Interactive widgets** in Colab notebooks.
- **CLI** (`ibm-bell-run`) powered by Typer.
- **FastAPI web service** with Docker support.
- Full **CI/CD** pipeline (tests, lint, type‑check, docs, releases).

## Quick start (Colab)
```python
%pip install -r https://raw.githubusercontent.com/<your‑repo>/main/requirements.txt
from ibm_bell import deps, service, experiment, visualization

deps.install(['qiskit','qiskit-ibm-runtime','matplotlib','numpy','ipywidgets'])
# set IBM_QUANTUM_TOKEN in Colab Secrets
cfg = experiment.SweepConfig(
    angles_a=[0, 0.5, 1.0],
    angles_b=[0, 0.5, 1.0],
    shots=1024,
    mitigation=['zne','readout'],
    tomography=False,
)
grid, backend = experiment.run_sweep(cfg)
visualization.plot_heatmap(grid, cfg.angles_a, cfg.angles_b)
```

## Installation (local)
```bash
git clone https://github.com/<your‑repo>.git
cd ibm-quantum-bell-explorer
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -e .
```

## Running the CLI
```bash
ibm-bell-run --grid 5 5 --shots 2048 --mitigation zne readout
```

## Development
```bash
pytest -q               # run tests
mypy ibm_bell           # static typing
ruff check ibm_bell      # lint
mkdocs serve            # view documentation locally
```