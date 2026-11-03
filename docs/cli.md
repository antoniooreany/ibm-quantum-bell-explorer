# Консольный интерфейс (CLI)

Пакет включает набор консольных утилит на базе Typer:

## 1. Запуск эксперимента: `ibm-bell-run`
```bash
# Базовый запуск с сеткой 5x5 и 1024 выстрелами
ibm-bell-run

# С кастомными параметрами и шумоподавлением
ibm-bell-run --grid-a 5 --grid-b 5 --shots 2048 --mitigation zne readout

# С принудительным указанием бэкенда
ibm-bell-run --backend ibm_brisbane
```

## 2. Управление токеном IBM Quantum: `ibm-bell-cred`
```bash
# Проверка наличия сохраненного токена
ibm-bell-cred

# Безопасное сохранение токена в системное хранилище OS (Keyring / Credential Manager)
ibm-bell-cred-set
```
