# Family Finance Planner

Built from `docs/spec.md`.

## CLI report

```bash
PYTHONPATH=src python -m family_finance.cli path/to/input.json
```

## Web app (registration + authorization)

```bash
PYTHONPATH=src python -m family_finance.web
```

Then open `http://localhost:8000` to register and log in. The dashboard now includes:
- account management (create/list accounts with balances)
- transaction management for expenses and income (e.g., salary)
- JSON snapshot report generation

## Test

```bash
PYTHONPATH=src pytest
```
