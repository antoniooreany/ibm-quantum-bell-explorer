# Разработка, методологии и CI/CD

Проект разработан в строгом соответствии с высокими инженерными стандартами:

## Методологии
1. **SDD (Specification-Driven Development)**:
   - Любая функциональность предварительно специфицируется в архитектурных планах (`spec_interactive_ui.md`).
2. **TDD (Test-Driven Development)**:
   - Поведение системы фиксируется автоматизированными тестами до и во время разработки компонентов.
3. **Gitflow**:
   - `main`: стабильные, готовые к релизу версии кода.
   - `develop`: ветка интеграции.
   - `feature/*`: тематические ветки функциональности, вливающиеся через Pull Requests.
4. **CI/CD (Continuous Integration / Continuous Deployment)**:
   - GitHub Actions автоматически запускает:
     - Тестирование на Python 3.11 (`pytest -q`, `coverage xml`).
     - Статический анализ типов (`mypy ibm_bell --strict`).
     - Линтинг (`ruff check ibm_bell`).
     - Сборку и публикацию документации (`mkdocs build`, deploy to GitHub Pages).

## Локальная разработка и валидация
```bash
# Клонирование и установка в venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# Запуск проверок качества
pytest -q
mypy ibm_bell
ruff check ibm_bell
```
