"""FastAPI Application providing an interactive web dashboard and REST API
for exploring the IBM Quantum Bell CHSH experiment.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ibm_bell import experiment, io
from ibm_bell.service import get_service

app = FastAPI(
    title="IBM Quantum Bell Explorer",
    description="Interactive UI & API for quantum entanglement and Bell inequality verification",
    version="0.1.0",
)

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class RunRequest(BaseModel):
    shots: int = Field(default=1024, ge=1, le=100000, description="Number of shots")
    grid_a: int = Field(default=5, ge=2, le=50, description="Steps for Alice's angle (0 to pi/2)")
    grid_b: int = Field(default=5, ge=2, le=50, description="Steps for Bob's angle (0 to pi/2)")
    backend: Optional[str] = Field(default=None, description="Explicit backend name or None for auto real QP")
    mitigation: Optional[list[str]] = Field(default=None, description="Mitigation techniques")
    tomography: bool = Field(default=False, description="State tomography flag")


@app.get("/api/theory")
def get_theory_overview():
    """Return quantum theory overview, formulas, and bounds."""
    return {
        "title": "CHSH Bell Inequality & Quantum Entanglement",
        "state": "|Phi+> = (|00> + |11>) / sqrt(2)",
        "formula": "S = E(a, b) - E(a, b') + E(a', b) + E(a', b')",
        "chsh_bound_classical": 2.0,
        "chsh_bound_tsirelson": 2.8284271247,  # 2 * sqrt(2)
        "description": (
            "Bell's theorem shows that no physical theory of local hidden variables can ever reproduce "
            "all of the predictions of quantum mechanics. For classical local realistic theories, |S| <= 2. "
            "Quantum mechanics allows violations up to Tsirelson's bound 2*sqrt(2) ~ 2.828."
        ),
        "steps": [
            {"step": 1, "name": "Entanglement Preparation", "desc": "Hadamard on qubit 0 followed by CNOT(0 -> 1) prepares the maximally entangled Bell pair."},
            {"step": 2, "name": "Alice's Measurement", "desc": "Alice rotates her qubit by angle theta_A using Ry(-2*theta_A) before Z-basis projection."},
            {"step": 3, "name": "Bob's Measurement", "desc": "Bob rotates his qubit by angle theta_B using Ry(-2*theta_B) before Z-basis projection."},
            {"step": 4, "name": "Correlation Calculation", "desc": "Correlation E(a,b) = (N_00 + N_11 - N_01 - N_10) / Total."},
        ],
    }


@app.get("/api/backends")
def list_backends():
    """List available IBM Quantum backends and their hardware attributes."""
    try:
        service = get_service()
        backends = service.backends()
        items = []
        for b in backends:
            items.append({
                "name": b.name,
                "is_simulator": getattr(b, "is_simulator", False),
                "num_qubits": getattr(b, "num_qubits", getattr(b.configuration(), "n_qubits", 0)),
                "operational": getattr(b.status(), "operational", True),
                "pending_jobs": getattr(b.status(), "pending_jobs", 0),
            })
        return items
    except Exception as e:
        return [{
            "name": "ibmq_qasm_simulator",
            "is_simulator": True,
            "num_qubits": 32,
            "operational": True,
            "pending_jobs": 0,
            "note": f"Service lookup notice: {e}",
        }]


@app.get("/api/results")
def list_results():
    """List historical experiment result files stored on disk."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RESULTS_DIR.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
    res = []
    for f in files:
        res.append({
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "modified": f.stat().st_mtime,
        })
    return res


@app.get("/api/results/{filename}")
def get_result(filename: str):
    """Retrieve contents of a specific results CSV file."""
    p = RESULTS_DIR / filename
    if not p.is_file() or not p.name.endswith(".csv"):
        raise HTTPException(status_code=404, detail="Result file not found")
    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        grid = [[float(v) for v in row if v.strip()] for row in reader if row]
    return {
        "filename": filename,
        "grid": grid,
    }


@app.post("/api/run")
def trigger_run(req: RunRequest):
    """Trigger a CHSH sweep experiment."""
    angles_a = [i * np.pi / 2 / (req.grid_a - 1) for i in range(req.grid_a)]
    angles_b = [i * np.pi / 2 / (req.grid_b - 1) for i in range(req.grid_b)]
    cfg = experiment.SweepConfig(
        angles_a=angles_a,
        angles_b=angles_b,
        shots=req.shots,
        mitigation=req.mitigation,
        tomography=req.tomography,
    )
    try:
        grid, backend_used = experiment.run_sweep(cfg, backend_name=req.backend)
        target_path = RESULTS_DIR / "grid.csv"
        saved_path = io.save_grid(grid, target_path)
        return {
            "status": "success",
            "backend_used": backend_used,
            "saved_path": str(saved_path),
            "angles_a": angles_a,
            "angles_b": angles_b,
            "grid": grid.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def index_page():
    """Serve the single-page application dashboard."""
    return HTML_CONTENT


def main():
    """CLI entrypoint to launch the web dashboard server."""
    import uvicorn
    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IBM Quantum Bell Explorer | Интерактивная квантовая лаборатория</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #131b2e;
      --card-highlight: #1a2540;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --accent-quantum: #8b5cf6;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --border: #1f293d;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding-bottom: 40px;
    }
    header {
      background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%);
      border-bottom: 1px solid var(--border);
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.5px;
    }
    .logo span {
      background: linear-gradient(135deg, #60a5fa, #c084fc);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .badge {
      display: inline-block;
      padding: 0.25rem 0.6rem;
      font-size: 0.75rem;
      border-radius: 9999px;
      font-weight: 600;
    }
    .badge-quantum { background: rgba(139, 92, 246, 0.2); color: #c084fc; border: 1px solid #8b5cf6; }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }

    .container {
      max-width: 1400px;
      margin: 1.5rem auto;
      padding: 0 1rem;
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 1.5rem;
    }
    @media (max-width: 960px) {
      .container { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }
    label {
      display: block;
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 0.25rem;
    }
    input, select {
      width: 100%;
      padding: 0.6rem 0.75rem;
      background: #0b0f19;
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text);
      font-size: 0.9rem;
      margin-bottom: 0.9rem;
    }
    input:focus, select:focus {
      outline: none;
      border-color: var(--accent);
    }
    button.btn {
      width: 100%;
      padding: 0.75rem 1rem;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: background 0.15s, transform 0.05s;
    }
    button.btn:hover { background: var(--accent-hover); }
    button.btn:active { transform: scale(0.98); }
    button.btn:disabled { background: #374151; cursor: not-allowed; }

    .btn-secondary {
      background: #1e293b;
      color: #93c5fd;
      border: 1px solid #334155;
      padding: 0.4rem 0.75rem;
      font-size: 0.8rem;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.15s;
    }
    .btn-secondary:hover {
      background: #334155;
    }

    .formula-box {
      background: #080c14;
      border: 1px dashed #2e384d;
      border-radius: 8px;
      padding: 0.85rem;
      font-family: "Courier New", monospace;
      font-size: 0.9rem;
      color: #93c5fd;
      margin-bottom: 1rem;
    }
    .step-item {
      display: flex;
      gap: 0.75rem;
      margin-bottom: 0.85rem;
      font-size: 0.85rem;
      background: rgba(255, 255, 255, 0.02);
      padding: 0.6rem;
      border-radius: 6px;
      border-left: 3px solid var(--accent-quantum);
    }
    .step-num {
      width: 24px;
      height: 24px;
      background: var(--accent-quantum);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.75rem;
      flex-shrink: 0;
    }

    .matrix-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      font-size: 0.85rem;
      text-align: center;
    }
    .matrix-table th, .matrix-table td {
      border: 1px solid var(--border);
      padding: 0.5rem;
    }
    .matrix-table th {
      background: #172138;
      color: var(--text-muted);
    }
    .val-cell {
      font-weight: 600;
      border-radius: 4px;
      transition: background 0.2s, transform 0.1s;
      cursor: default;
    }
    .val-cell:hover {
      transform: scale(1.05);
      outline: 1px solid #60a5fa;
      z-index: 2;
    }

    .history-list {
      max-height: 220px;
      overflow-y: auto;
      list-style: none;
    }
    .history-item {
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.85rem;
      cursor: pointer;
      border-radius: 6px;
      margin-bottom: 0.25rem;
      transition: background 0.15s;
    }
    .history-item:hover { background: #1e293b; }
    .history-item.active { background: #2563eb; color: #fff; }

    #logBox {
      background: #080c14;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.75rem;
      font-family: monospace;
      font-size: 0.8rem;
      color: #10b981;
      min-height: 52px;
      max-height: 120px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 1.25rem;
    }
    .kpi-card {
      background: #0d1527;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.85rem;
      text-align: center;
    }
    .kpi-value {
      font-size: 1.4rem;
      font-weight: 700;
      color: #60a5fa;
      margin-top: 0.25rem;
    }
    .kpi-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
    }

    .chsh-banner {
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(59, 130, 246, 0.15));
      border: 1px solid #8b5cf6;
      border-radius: 8px;
      padding: 0.9rem;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
  </style>
</head>
<body>

<header>
  <div class="logo">
    <span>⚛ IBM Quantum Bell Explorer</span>
    <div class="badge badge-quantum">Hardware-First Engine</div>
  </div>
  <div style="font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center; gap: 1rem;">
    <span>Статус: <strong id="systemStatus" style="color: #34d399;">● Готов к квантовому эксперименту</strong></span>
    <button class="btn-secondary" onclick="loadBackends()">🔄 Обновить процессоры</button>
  </div>
</header>

<div class="container">
  <!-- Left Control Panel -->
  <div>
    <div class="card">
      <div class="card-title">⚙ Параметры эксперимента</div>

      <label for="shots">Число измерений (Shots):</label>
      <input type="number" id="shots" value="256" min="64" max="10000" step="64">

      <label for="gridA">Сетка углов Алисы θ_A (шагов от 0 до π/2):</label>
      <input type="number" id="gridA" value="3" min="2" max="15">

      <label for="gridB">Сетка углов Боба θ_B (шагов от 0 до π/2):</label>
      <input type="number" id="gridB" value="3" min="2" max="15">

      <label for="backendSelect">Выбор квантового процессора:</label>
      <select id="backendSelect">
        <option value="">Авто: Least Busy Real QP (Реальный процессор)</option>
      </select>

      <button id="runBtn" class="btn" onclick="executeSweep()">
        🚀 Запустить на квантовом компьютере
      </button>

      <div style="margin-top: 1rem;">
        <label>Журнал квантовых событий:</label>
        <div id="logBox">Ожидание запуска эксперимента...</div>
      </div>
    </div>

    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <div class="card-title" style="margin-bottom: 0; border-bottom: none; padding-bottom: 0;">📁 История запусков</div>
        <button class="btn-secondary" onclick="loadHistory()">Обновить</button>
      </div>
      <ul id="historyList" class="history-list">
        <li style="color: var(--text-muted); padding: 0.5rem;">Загрузка истории...</li>
      </ul>
    </div>
  </div>

  <!-- Right Dashboard & Educational View -->
  <div>
    <div class="card">
      <div class="card-title">📖 Квантовое объяснение (Теория и неравенство Белла CHSH)</div>

      <div class="chsh-banner">
        <div>
          <div style="font-size: 0.95rem; font-weight: 600; color: #f3f4f6;">Проверка локального реализма:</div>
          <div style="font-size: 0.85rem; color: #9ca3af;">Классический предел: <strong>|S| ≤ 2</strong> | Предел квантовой механики (Цирельсона): <strong>|S| ≤ 2√2 ≈ 2.8284</strong></div>
        </div>
        <div id="violationBadge" class="badge badge-quantum" style="font-size: 0.85rem; padding: 0.35rem 0.8rem;">Ожидание вычисления S</div>
      </div>

      <div class="formula-box">
        Состояние: |Φ⁺⟩ = (|00⟩ + |11⟩) / √2<br>
        Корреляция: E(a,b) = (N₀₀ + N₁₁ - N₀₁ - N₁₀) / N_total<br>
        Параметр Белла: S = E(a, b) - E(a, b') + E(a', b) + E(a', b')
      </div>

      <div id="theorySteps"></div>
    </div>

    <!-- Active Analytics KPIs -->
    <div class="kpi-grid" id="kpiSection" style="display: none;">
      <div class="kpi-card">
        <div class="kpi-label">Макс. параметр CHSH (S)</div>
        <div class="kpi-value" id="kpiSVal">-</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Мин. корреляция E(a,b)</div>
        <div class="kpi-value" id="kpiMinE">-</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Макс. корреляция E(a,b)</div>
        <div class="kpi-value" id="kpiMaxE">-</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Использованный бэкенд</div>
        <div class="kpi-value" id="kpiBackend" style="font-size: 1rem; color: #a78bfa; margin-top: 0.5rem;">-</div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">📊 Матрица корреляций ⟨A(θ_A) B(θ_B)⟩</div>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
        Тепловая карта квантовой корреляции: от синего (-1.0, антикорреляция) до зеленого (+1.0, корреляция).
      </p>

      <div style="position: relative; height: 300px; width: 100%; margin-bottom: 1rem;">
        <canvas id="correlationChart"></canvas>
      </div>

      <div id="matrixContainer"></div>
    </div>
  </div>
</div>

<script>
  let chartInstance = null;

  async function loadTheory() {
    try {
      const res = await fetch('/api/theory');
      const data = await res.json();
      const cont = document.getElementById('theorySteps');
      cont.innerHTML = data.steps.map(s => `
        <div class="step-item">
          <div class="step-num">${s.step}</div>
          <div><strong>${s.name}:</strong> ${s.desc}</div>
        </div>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  }

  async function loadBackends() {
    const sel = document.getElementById('backendSelect');
    try {
      const res = await fetch('/api/backends');
      const backends = await res.json();
      sel.innerHTML = '<option value="">Авто: Least Busy Real QP (Реальный процессор)</option>';
      backends.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.name;
        opt.textContent = `${b.name} (${b.is_simulator ? 'Симулятор' : 'Реальный QP'}, ${b.num_qubits} кубитов, очередь: ${b.pending_jobs || 0})`;
        sel.appendChild(opt);
      });
    } catch (e) {
      console.warn("Backends fetch error", e);
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/results');
      const files = await res.json();
      const list = document.getElementById('historyList');
      if (files.length === 0) {
        list.innerHTML = '<li style="padding: 0.5rem; color: #9ca3af;">Нет сохраненных прогонов</li>';
        return;
      }
      list.innerHTML = files.map(f => `
        <li class="history-item" onclick="loadResult('${f.filename}', this)">
          <span>📄 ${f.filename}</span>
          <span style="font-size: 0.75rem; color: #9ca3af;">${(f.size_bytes / 1024).toFixed(1)} KB</span>
        </li>
      `).join('');
    } catch (e) {
      console.error(e);
    }
  }

  function computeMaxCHSH(grid) {
    if (!grid || grid.length < 2 || grid[0].length < 2) return null;
    let maxS = 0;
    // Iterate over all pairs of Alice and Bob angles
    for (let i = 0; i < grid.length; i++) {
      for (let ip = 0; ip < grid.length; ip++) {
        if (i === ip) continue;
        for (let j = 0; j < grid[0].length; j++) {
          for (let jp = 0; jp < grid[0].length; jp++) {
            if (j === jp) continue;
            const E_ab  = grid[i][j];
            const E_abp = grid[i][jp];
            const E_apb = grid[ip][j];
            const E_apbp = grid[ip][jp];
            const S = Math.abs(E_ab - E_abp + E_apb + E_apbp);
            if (S > maxS) maxS = S;
          }
        }
      }
    }
    return maxS;
  }

  function updateKPIs(grid, backendName) {
    if (!grid || !grid.length) return;
    document.getElementById('kpiSection').style.display = 'grid';

    let flat = grid.flat();
    let minE = Math.min(...flat);
    let maxE = Math.max(...flat);
    let maxS = computeMaxCHSH(grid);

    document.getElementById('kpiMinE').innerText = minE.toFixed(3);
    document.getElementById('kpiMaxE').innerText = maxE.toFixed(3);
    document.getElementById('kpiBackend').innerText = backendName || "Real QP (Least Busy)";

    const badge = document.getElementById('violationBadge');
    if (maxS !== null) {
      document.getElementById('kpiSVal').innerText = maxS.toFixed(4);
      if (maxS > 2.0) {
        badge.className = 'badge badge-success';
        badge.innerHTML = `🔥 Нарушение доказано! S = ${maxS.toFixed(3)} > 2.0`;
      } else {
        badge.className = 'badge badge-quantum';
        badge.innerHTML = `S = ${maxS.toFixed(3)} (в пределах классики)`;
      }
    } else {
      document.getElementById('kpiSVal').innerText = "Сетка < 2x2";
    }
  }

  async function loadResult(filename, el) {
    try {
      if (el) {
        document.querySelectorAll('.history-item').forEach(i => i.classList.remove('active'));
        el.classList.add('active');
      }
      const res = await fetch(`/api/results/${filename}`);
      const data = await res.json();
      renderMatrix(data.grid);
      renderChart(data.grid);
      updateKPIs(data.grid, filename.includes("simulator") ? "ibmq_qasm_simulator" : "Hardware Execution");
      document.getElementById('logBox').innerText = `Загружен исторический файл: ${filename}`;
    } catch (e) {
      alert("Ошибка загрузки файла: " + e);
    }
  }

  function getColorForValue(v) {
    if (v >= 0) {
      const intensity = Math.min(1, v);
      return `rgba(16, 185, 129, ${0.15 + intensity * 0.75})`;
    } else {
      const intensity = Math.min(1, Math.abs(v));
      return `rgba(59, 130, 246, ${0.15 + intensity * 0.75})`;
    }
  }

  function renderMatrix(grid) {
    if (!grid || !grid.length) return;
    let html = '<table class="matrix-table"><thead><tr><th>θ_A \\ θ_B</th>';
    for (let j = 0; j < grid[0].length; j++) {
      html += `<th>Шаг ${j+1}</th>`;
    }
    html += '</tr></thead><tbody>';
    for (let i = 0; i < grid.length; i++) {
      html += `<tr><th>Шаг ${i+1}</th>`;
      for (let j = 0; j < grid[i].length; j++) {
        const val = grid[i][j];
        const bg = getColorForValue(val);
        html += `<td class="val-cell" style="background: ${bg};" title="E(θ_A[${i}], θ_B[${j}]) = ${val.toFixed(4)}">${val.toFixed(4)}</td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table>';
    document.getElementById('matrixContainer').innerHTML = html;
  }

  function renderChart(grid) {
    const ctx = document.getElementById('correlationChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    const colors = ['#60a5fa', '#c084fc', '#34d399', '#f59e0b', '#ec4899', '#38bdf8', '#fb7185'];
    const datasets = grid.map((row, idx) => ({
      label: `Угол Алисы θ_A #${idx+1}`,
      data: row,
      borderColor: colors[idx % colors.length],
      backgroundColor: 'transparent',
      borderWidth: 2.5,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 6
    }));

    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: grid[0].map((_, j) => `θ_B #${j+1}`),
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { labels: { color: '#f3f4f6', font: { size: 12 } } },
          tooltip: {
            backgroundColor: '#0f172a',
            borderColor: '#3b82f6',
            borderWidth: 1,
            titleColor: '#60a5fa',
            bodyColor: '#f3f4f6'
          }
        },
        scales: {
          x: { ticks: { color: '#9ca3af' }, grid: { color: '#1f293d' } },
          y: { min: -1.05, max: 1.05, ticks: { color: '#9ca3af' }, grid: { color: '#1f293d' } }
        }
      }
    });
  }

  async function executeSweep() {
    const btn = document.getElementById('runBtn');
    const log = document.getElementById('logBox');
    btn.disabled = true;
    log.innerText = "⏳ Формирование квантовых схем...\\nОтправка в Qiskit Runtime Service...\\nПоиск наименее загруженного квантового процессора...";

    const payload = {
      shots: parseInt(document.getElementById('shots').value, 10),
      grid_a: parseInt(document.getElementById('gridA').value, 10),
      grid_b: parseInt(document.getElementById('gridB').value, 10),
      backend: document.getElementById('backendSelect').value || null
    };

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Execution failed");

      log.innerText = `✅ Успешно выполнено на процессоре: ${data.backend_used}\\nСохранено в файл: ${data.saved_path}`;
      renderMatrix(data.grid);
      renderChart(data.grid);
      updateKPIs(data.grid, data.backend_used);
      await loadHistory();
    } catch (e) {
      log.innerText = `❌ Ошибка выполнения: ${e.message}`;
    } finally {
      btn.disabled = false;
    }
  }

  // Initial bootstrap
  loadTheory();
  loadBackends();
  loadHistory();
</script>

</body>
</html>
"""
