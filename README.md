# IBM Quantum Bell Explorer

[![CI Pipeline](https://github.com/antoniooreany/ibm-quantum-bell-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/antoniooreany/ibm-quantum-bell-explorer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://www.python.org/)

Комплексный, модульный Python-пакет и интерактивная лаборатория для демонстрации квантовой запутанности и экспериментальной проверки нарушения **неравенства Белла (CHSH)** на реальных квантовых процессорах **IBM Quantum** (или симуляторах).

Проект разработан в строгом соответствии с дисциплинами **SDD (Specification-Driven Development)**, **TDD (Test-Driven Development)**, **Gitflow** и непрерывной интеграцией **CI/CD**.

---

## 🌟 Ключевые возможности

- 🚀 **Hardware-First подход**: Эксперимент по умолчанию запускается на наименее загруженном **реальном квантовом процессоре IBM Quantum** (`simulator=False`). Квантовый симулятор (`ibmq_qasm_simulator`) задействуется только при отсутствии доступа к реальному железу или исчерпании квот.
- 🖥️ **Интерактивный Web UI дашборд**: Полнофункциональный одностраничный веб-интерфейс на **FastAPI + Chart.js**:
  - Наглядное пошаговое объяснение теории и квантовой схемы Белла.
  - Управление параметрами sweep (число выстрелов, сетка углов Алисы и Боба $\theta_A, \theta_B$).
  - Выбор бэкенда с отображением статуса, количества кубитов и очереди задач.
  - Интерактивный калькулятор нарушения неравенства CHSH ($S \le 2$ классика, $S \le 2\sqrt{2}$ Цирельсон).
  - Тепловая цветовая матрица корреляций и графики срезов углов.
  - История запусков с возможностью мгновенного просмотра прошлых результатов.
- 🕒 **Версионирование результатов с таймстемпами**: Каждый прогон автоматически сохраняет результат как в базовый `results/grid.csv`, так и в отдельный файл с временной меткой: `results/grid_YYYYMMDD_HHMMSS.csv`.
- 🔐 **Безопасная работа с учетными данными**:
  - Поддержка системного защищенного хранилища OS (`Keyring` / Windows Credential Manager).
  - Поддержка Google Colab Secrets (`userdata`).
  - Переменная окружения `IBM_QUANTUM_TOKEN`.
- ⚡ **CLI утилиты**: Удобные консольные команды (`ibm-bell-run`, `ibm-bell-web`, `ibm-bell-cred`, `ibm-bell-cred-set`).
- 🤖 **CI/CD на GitHub Actions**: Автоматическое тестирование, проверка покрытия (`coverage`), линтинг (`ruff`), типизация (`mypy`) и публикация документации (`MkDocs Material`).

---

## 🛠️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/antoniooreany/ibm-quantum-bell-explorer.git
cd ibm-quantum-bell-explorer
```

### 2. Создание виртуального окружения и установка
```bash
python -m venv .venv
# Активация на Windows:
.venv\Scripts\activate
# Активация на Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

### 3. Настройка токена IBM Quantum
Получите бесплатный токен API в консоли [IBM Quantum Platform](https://quantum.ibm.com/):
```bash
# Через консольную утилиту пакета:
ibm-bell-cred-set

# Либо через переменную окружения:
export IBM_QUANTUM_TOKEN="ваш_токен_ibm"   # Linux/macOS
set IBM_QUANTUM_TOKEN="ваш_токен_ibm"      # Windows cmd
$env:IBM_QUANTUM_TOKEN="ваш_токен_ibm"     # Windows PowerShell
```

---

## 🖥️ Использование

### Запуск интерактивного Web-дашборда
```bash
ibm-bell-web
```
Откройте браузер по адресу: **`http://localhost:8000`**

В дашборде доступны:
- Выбор квантового бэкенда (автоматический поиск наименее загруженного реального процессора или выбор симулятора).
- Настройка параметров свипа ($\theta_A, \theta_B$ от $0$ до $\pi/2$).
- Вычисление максимума CHSH параметра $S$.
- Панель истории всех запусков.

### Запуск через консоль (CLI)
```bash
# Быстрый запуск с параметрами по умолчанию
ibm-bell-run

# Запуск с детальной сеткой углов и шумоподавлением
ibm-bell-run --grid-a 5 --grid-b 5 --shots 2048 --mitigation zne readout

# Принудительный выбор конкретного бэкенда
ibm-bell-run --backend ibm_brisbane
```

---

## 📚 Теория: Эксперимент Белла (CHSH)

Квантовая схема эксперимента готовит максимально запутанную пару кубитов (состояние Белла $|\Phi^+\rangle$):
$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

Затем Алиса и Боб поворачивают базисы своих измерений на углы $\theta_A$ и $\theta_B$:
- Алиса выполняет гейт $R_y(-2\theta_A)$.
- Боб выполняет гейт $R_y(-2\theta_B)$.

По результатам серии выстрелов (*shots*) рассчитывается квантовая корреляция:
$$E(\theta_A, \theta_B) = \frac{N_{00} + N_{11} - N_{01} - N_{10}}{N_{total}}$$

Параметр CHSH:
$$S = E(a, b) - E(a, b') + E(a', b) + E(a', b')$$

- **Классический предел (локальный реализм)**: $|S| \le 2$
- **Квантовый предел Цирельсона**: $|S| \le 2\sqrt{2} \approx 2.8284$

Превышение значения $2.0$ экспериментально доказывает квантовую нелокальность и отсутствие скрытых локальных параметров.

---

## 🧪 Разработка, тестирование и Gitflow

### Запуск тестов и линтера
```bash
# Модульные тесты
pytest -q

# Проверка типов
mypy ibm_bell

# Линтинг и качество кода
ruff check ibm_bell web cli
```

### Gitflow правила репозитория
- `main` — только проверенные и готовые релизы.
- `develop` — ветка интеграции.
- `feature/*` — ветки разработки новых фичей, вливающиеся в `develop` через PR.
- Автоматический CI проверяет каждый пуш в `main` и `develop`.

---

## 📄 Лицензия
Проект распространяется под открытой лицензией [MIT](LICENSE).
