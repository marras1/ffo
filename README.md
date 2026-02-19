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

Then open `http://localhost:8000` to register, log in, and generate reports from JSON snapshots.

## Test

```bash
PYTHONPATH=src pytest
```
