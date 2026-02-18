# Contributing

Thanks for contributing to Swali-AI.

## 1) Local Setup

```bash
git clone <repo-url>
cd swali-ai
poetry install --with dev
cd frontend && npm install && cd ..
```

## 2) Common Commands

Prefer using the `Makefile`:

```bash
make help
make test
make lint
make format
make run-backend
make run-frontend
make process-data
make collect-ai-ml
make experiments
```

## 3) Pre-commit Hooks

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Hooks configured in `.pre-commit-config.yaml` run:
- `ruff` checks/fixes
- `ruff-format`
- basic hygiene checks (YAML, EOF, whitespace, large files)

## 4) Docker Dev Workflow

```bash
docker compose -f docker-composer.dev.yml up --build
```

Services:
- `backend` on `http://localhost:8000`
- `frontend` on `http://localhost:5173`

## 5) Testing Expectations

- Add or update tests for behavior changes.
- Keep tests deterministic and fast where possible.
- Run at least targeted tests before opening a PR.

## 6) Documentation Expectations

Update relevant docs when behavior changes:
- `README.md`
- `experiments.md`
- `progress.md`
- `docs/architecture.md`

## 7) Pull Request Checklist

- [ ] Tests pass locally (`make test`).
- [ ] Lint/format pass (`make lint`, `make format`).
- [ ] New behavior is documented.
- [ ] No unrelated files are changed.
- [ ] Security-sensitive changes noted in `security.md`.
